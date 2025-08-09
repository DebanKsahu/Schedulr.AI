from sqlmodel import SQLModel

class ScheduleRequest(SQLModel):
    thread_id: str
    user_query: str

class ScheduleResponse(SQLModel):
    thread_id: str
    response: str
    is_final: str