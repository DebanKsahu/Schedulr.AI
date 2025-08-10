import asyncio
from datetime import datetime, timedelta, timezone
from typing import List
import pytz
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from sqlalchemy.ext.asyncio import AsyncSession
import tzlocal

from app.core.config import Settings
from app.core.utils.utility_functions import UtilityContainer
from app.database.models.user_info_models import UserInDB
import httpx

class GooglePeopleService():

    def __init__(self, session: AsyncSession, settings: Settings, user: UserInDB):
        self.session = session
        self.user = user
        self.client_id = settings.CLIENT_ID
        self.client_secret = settings.CLIENT_SECRET
        self.token_url=settings.TOKEN_URL
        self.scopes = settings.SCOPES
        self.free_busy_url = "https://www.googleapis.com/calendar/v3/freeBusy"
        self.calendar_base_url = "https://www.googleapis.com/calendar/v3"

    async def get_credentials(self):
        access_token = self.user.access_token
        refresh_token = self.user.refresh_token
        expire_time = self.user.expire_time
        if expire_time.tzinfo is None:
            expire_time = expire_time.replace(tzinfo=timezone.utc)
        curr_time = datetime.now(timezone.utc)

        if curr_time>=(expire_time-timedelta(seconds=60)):
            creds = Credentials(
                token = None,
                refresh_token=refresh_token,
                token_uri=self.token_url,
                client_id=self.client_id,
                client_secret=self.client_secret,
                scopes=self.scopes
            )
            await asyncio.to_thread(creds.refresh, Request())
            access_token = creds.token
            expire_in=creds.expiry
            credentials_dict = {
                "user_id": self.user.user_id,
                "email": self.user.email,
                "name": self.user.name,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expire_in": expire_in
            }
            await UtilityContainer.update_credenctials_to_db(session=self.session, credentials=credentials_dict)
        return Credentials(
            token=access_token,
            refresh_token=refresh_token,
            client_id=self.client_id,
            client_secret=self.client_secret,
            scopes=self.scopes
        )
    
    def call_people_api(self, creds: Credentials, user_query: str):
        service = build("people", "v1", credentials=creds)
        result = service.people().searchContacts(
            query=user_query,
            readMask="names,emailAddresses"
        ).execute()
        return result
    
    async def search_contacts(self, user_query: str):
        creds = await self.get_credentials()
        results = await asyncio.to_thread(self.call_people_api,creds,user_query)
        contacts: List[dict] = []
        for person in results.get("results", []):
            name = person["person"].get("names", [{}])[0].get("displayName","")
            email = person["person"].get("emailAddresses", [{}])[0].get("value","")
            contacts.append({"name": name, "email": email})
        return contacts
    
    async def check_time_slots(self, time_min: str, time_max: str, calendar_ids: List[str] = ["primary"]) -> dict:
        creds = await self.get_credentials()
        access_token = creds.token
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        body = {
            "timeMin": time_min,
            "timeMax": time_max,
            "items": [{"id": cal_id} for cal_id in calendar_ids]
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=self.free_busy_url,
                json=body,
                headers=headers
            )
            response.raise_for_status()
            return response.json().get("calendars", {})
        
    async def create_event(self, summary: str, start_time: datetime, end_time: datetime, participants: dict, description: str | None = None, location: str | None = None):
        if description is None:
            description=""
        if location is None:
            location=""
        creds = await self.get_credentials()
        access_token = creds.token
        headers = {"Authorization": f"Bearer {access_token}"}
        timezone = tzlocal.get_localzone_name()
        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=pytz.timezone(timezone))
        if end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=pytz.timezone(timezone))
        event_body = {
            "summary": summary,
            "location": location,
            "description": description,
            "start": {"dateTime": start_time.isoformat(), "timeZone": timezone},
            "end": {"dateTime": end_time.isoformat(), "timeZone": timezone},
            "attendees": [{"email": email} for email in participants.get("resolved_participants",{}).values()] if participants.get("resolved_participants",None) else []
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.calendar_base_url}/calendars/primary/events",
                json=event_body,
                headers=headers
            )
            resp.raise_for_status()
            return resp.json()