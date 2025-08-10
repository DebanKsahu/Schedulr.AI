from datetime import datetime
from sqlmodel import SQLModel, Field

class UserInDB(SQLModel, table=True):
    user_id: str = Field(primary_key=True, min_length=1)
    email: str = Field(unique=True, min_length=1)
    name: str = Field(min_length=1)
    access_token: str = Field(min_length=1)
    refresh_token: str = Field(min_length=1)
    expire_time: datetime 