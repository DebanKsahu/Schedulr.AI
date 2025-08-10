from app.database.models.schedule_models import ScheduleRequest
from langchain_core.messages import BaseMessage
from sqlalchemy.ext.asyncio import AsyncSession

class ScheduleAgentInput(ScheduleRequest):
    session: AsyncSession

    model_config = {
        "arbitrary_types_allowed": True
    }

class ScheduleAgentIntent(ScheduleAgentInput):
    is_scheduling_intent: bool

class ScheduleAgentEntityExtraction(ScheduleAgentInput):
    entity_extraction_chain_message: BaseMessage

class ScheduleAgentOutput(ScheduleRequest):
    llm_response: str

class ScheduleAgentOverallState(
    ScheduleAgentIntent,
    ScheduleAgentEntityExtraction,
    ScheduleAgentOutput
):
    pass
