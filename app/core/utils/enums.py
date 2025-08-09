from enum import Enum, EnumCheck

class ResponseType(str, Enum):
    SUCCESS = "Successful Response"
    FAIL = "Failed Response"