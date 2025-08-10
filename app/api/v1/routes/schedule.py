from fastapi import APIRouter, Depends

from app.core.utils.dependency import DependencyContainer
from app.database.models.schedule_models import ScheduleRequest
from app.database.models.graph_states.scheduling_agent_states import ScheduleAgentInput
from app.agent.scheduling_agent import graph
from sqlalchemy.ext.asyncio import AsyncSession

schedule_router = APIRouter(
    prefix="/schedule/v1",
    tags=["Agent", "Scheduling"]
)

@schedule_router.post("/schedule_agent")
async def chat_with_scheduling_agent(user_request: ScheduleRequest, token: str = Depends(DependencyContainer.oauth2_scheme), session: AsyncSession = Depends(DependencyContainer.get_session)):
    agent_response = await graph.ainvoke(
        input=ScheduleAgentInput(
            user_id=user_request.user_id,
            thread_id=user_request.thread_id,
            user_query=user_request.user_query,
            session=session
        )
    )
    return agent_response