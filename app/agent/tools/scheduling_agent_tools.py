from datetime import date, time
from typing import List

from langchain.tools import tool
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.utils.dependency import DependencyContainer
from app.database.models.user_info_models import UserInDB
from app.services.google_people_service import GooglePeopleService


class ScheduleEventTool(BaseModel):
    """Tool to capture details for scheduling a calendar event."""
    title: str = Field(..., description="The title or summary of the event.")
    participants: List[str] = Field(..., description="A list of the names of the people to invite.")
    event_date: date = Field(..., description="The date of the event in YYYY-MM-DD format.")
    event_time: time = Field(..., description="The time of the event in HH:MM:SS format.")
    duration_minutes: int | None = Field(default=60, description="The duration of the event in minutes. Defaults to 60.")
    location: str | None = Field(default=None, description="The physical location or 'Google Meet' for a virtual meeting.")
    description: str | None = Field(default=None, description="A brief description or agenda for the meeting, extracted from the user's purpose.")

async def participant_resolver(participants: List[str], session: AsyncSession, user_id: str):
    resolved_participants = {}
    if participants is not None:
        user = await session.get(UserInDB,user_id)
        if user is not None:
            google_people_service = GooglePeopleService(
                session=session,
                settings=settings,
                user=user
            )
            for participant in participants:
                contacts = await google_people_service.search_contacts(user_query=participant)
                if len(contacts)>=1:
                    for contact in contacts:
                        resolved_participants[contact.get("name","Unknown")]=contact.get("email","Unknown")
        else:
            raise ValueError("No user Found")
    return {
        "resolved_participants": resolved_participants
    }

@tool(args_schema=ScheduleEventTool)
async def scheduling_tool(
    title: str, 
    participants: List[str], 
    event_date: date, 
    event_time: time, 
    duration_minutes: int | None, 
    location: str | None, 
    description: str | None
):
    pass