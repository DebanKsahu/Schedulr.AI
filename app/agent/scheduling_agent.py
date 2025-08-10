from datetime import datetime, timedelta, timezone
import json

from langgraph.graph import END, START, StateGraph

from app.agent.prompt_templates.scheduling_agent_prompt_templates import (
    entity_extraction_template,
    intent_validation_template,
    schedule_response_template
)
from app.agent.tools.scheduling_agent_tools import participant_resolver, scheduling_tool
from app.core.utils.llm_models import google_gemini
from app.core.utils.utility_functions import UtilityContainer
from app.database.models.graph_states.scheduling_agent_states import (
    ScheduleAgentEntityExtraction,
    ScheduleAgentInput,
    ScheduleAgentIntent,
    ScheduleAgentOutput,
    ScheduleAgentOverallState,
)
from app.database.models.output_formatter import IntentClassificationOutput
from app.database.models.user_info_models import UserInDB
from app.services.google_people_service import GooglePeopleService
from app.core.config import settings


async def check_intent(state: ScheduleAgentInput) -> ScheduleAgentIntent:
    llm_chain = (intent_validation_template | google_gemini.with_structured_output(IntentClassificationOutput))
    result = await llm_chain.ainvoke({
        "query": state.user_query
    })
    intent_info = IntentClassificationOutput.model_validate(result)
    return ScheduleAgentIntent(
        user_id=state.user_id,
        thread_id=state.thread_id,
        user_query=state.user_query,
        session=state.session,
        is_scheduling_intent=intent_info.is_scheduling_intent
    )

def intent_conditional_route(state: ScheduleAgentIntent):
    if state.is_scheduling_intent:
        return "entity_extraction"
    else:
        return "wrong_intent"
    
async def wrong_intent(state: ScheduleAgentIntent) -> ScheduleAgentOutput:
    return ScheduleAgentOutput(
        user_id=state.user_id,
        thread_id=state.thread_id,
        user_query=state.user_query,
        llm_response="This is not a scheduling query"
    )

async def entity_extraction(state: ScheduleAgentIntent) -> ScheduleAgentEntityExtraction:
    local_zone = datetime.now().astimezone().tzinfo
    current_datetime = datetime.now(local_zone)
    llm_chain = (entity_extraction_template | google_gemini.bind_tools(tools=[scheduling_tool],tool_choice="scheduling_tool"))
    result = await llm_chain.ainvoke({
        "current_date": str(current_datetime.date()),
        "current_time": str(current_datetime.time()),
        "user_timezone": UtilityContainer.get_utc_offset_string(),
        "query": state.user_query
    })
    return ScheduleAgentEntityExtraction(
        user_id=state.user_id,
        thread_id=state.thread_id,
        user_query=state.user_query,
        session=state.session,
        entity_extraction_chain_message=result
    )

async def schedule_node_call(state: ScheduleAgentEntityExtraction) -> ScheduleAgentOutput:
    title=None 
    participants=None 
    event_date=None 
    event_time=None
    duration_minutes=None 
    location=None
    description=None
    for key,value in state.entity_extraction_chain_message:
        if key=="tool_calls":
            for call_info in value:
                tool_name = call_info.get("name",None)
                if tool_name is not None and tool_name=="scheduling_tool":
                    kwargs = call_info.get("args",{})
                    participants=kwargs.get("participants",None) 
                    title=kwargs.get("title",None) 
                    event_date=kwargs.get("event_date",None)
                    event_time=kwargs.get("event_time",None)
                    duration_minutes=kwargs.get("duration_minutes",None) 
                    location=kwargs.get("location",None)
                    description=kwargs.get("description",None)

    if title is not None and event_date is not None and event_time is not None and participants is not None:
        partcipants_dict = await participant_resolver(participants=participants,session=state.session,user_id=state.user_id)
        user = await state.session.get(UserInDB,state.user_id)
        if user is not None:
            google_service = GooglePeopleService(
                session=state.session,
                settings=settings,
                user=user
            )
            if duration_minutes is None:
                duration_minutes = 60
            start_dt = datetime.fromisoformat(f"{event_date}T{event_time}")
            end_dt = start_dt + timedelta(minutes=duration_minutes)
            time_min = start_dt.replace(tzinfo=timezone.utc).isoformat()
            time_max = end_dt.replace(tzinfo=timezone.utc).isoformat()
            about_slot = await google_service.check_time_slots(time_min=time_min,time_max=time_max)
            has_conflict = any(bool(calendar_data.get("busy",[])) for calendar_data in about_slot.values())
            calender_api_response = ""
            if not has_conflict:
                calender_api_response = await google_service.create_event(
                    summary=title,
                    start_time=start_dt,
                    end_time=end_dt,
                    participants=partcipants_dict,
                    description=description,
                    location=location
                )
            else:
                all_busy_slots = []
                for calendar_data in about_slot.values():
                    all_busy_slots.extend(calendar_data.get("busy",[]))
                calender_api_response = {
                    "status": "failed",
                    "summary": title,
                    "busy": all_busy_slots
                }
            llm_chain = (schedule_response_template | google_gemini)
            result = await llm_chain.ainvoke({
                "user_input": json.dumps(calender_api_response,indent=2)
            })
            await state.session.close()
            return ScheduleAgentOutput(
                user_id=state.user_id,
                thread_id=state.thread_id,
                user_query=state.user_query,
                llm_response=str(result.content)
            )
        else:
            await state.session.close()
            return ScheduleAgentOutput(
                user_id=state.user_id,
                thread_id=state.thread_id,
                user_query=state.user_query,
                llm_response=f"User with user_id:{state.user_id} don't exist"
            )
    else:
        await state.session.close()
        return ScheduleAgentOutput(
            user_id=state.user_id,
            thread_id=state.thread_id,
            user_query=state.user_query,
            llm_response="Query Intent is not clear"
        )
graph_builder = StateGraph(
    state_schema=ScheduleAgentOverallState,
    input_schema=ScheduleAgentInput,
    output_schema=ScheduleAgentOutput
)
graph_builder.add_node("check_intent",check_intent)
graph_builder.add_node("wrong_intent",wrong_intent)
graph_builder.add_node("entity_extraction",entity_extraction)
graph_builder.add_node("schedule_node_call",schedule_node_call)

graph_builder.add_edge(START,"check_intent")
graph_builder.add_conditional_edges("check_intent",intent_conditional_route)
graph_builder.add_edge("wrong_intent",END)
graph_builder.add_edge("entity_extraction","schedule_node_call")
graph_builder.add_edge("schedule_node_call",END)
graph = graph_builder.compile()