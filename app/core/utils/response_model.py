from typing import Any
from pydantic import BaseModel

from app.core.utils.enums import ResponseType

class APIResponse(BaseModel):
    status: ResponseType
    message: str | None
    data: Any | None

    @classmethod
    def successful_response(cls, message: str | None = None, data: Any | None = None):
        return cls(
            status=ResponseType.SUCCESS,
            message=message,
            data=data
        )
    
    @classmethod
    def unsuccessful_response(cls, message: str | None = None, data: Any | None = None):
        return cls(
            status=ResponseType.FAIL,
            message=message,
            data=data
        )