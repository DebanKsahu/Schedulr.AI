from pydantic import BaseModel

class ScheduleRequest(BaseModel):
    user_id: str
    thread_id: str
    user_query: str

class ScheduleResponse(BaseModel):
    user_id: str
    thread_id: str
    response: str
    is_final: str