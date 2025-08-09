from typing import List
from pydantic_settings import BaseSettings

class GoogleServiceSettings(BaseSettings):
    CLIENT_ID: str
    PROJECT_ID: str
    AUTH_URL: str
    TOKEN_URL: str
    AUTH_PROVIDER_X509_CERT_URL: str
    CLIENT_SECRET: str
    SERVER_METADATA_URL: str
    SCOPES: List[str] = [
        "openid",
        "email",
        "profile",
        "https://www.googleapis.com/auth/calendar.events",
        "https://www.googleapis.com/auth/contacts.readonly"
    ]
    REDIRECT_URLS: List[str] = [

    ]

class DBSettings(BaseSettings):
    DB_URL: str

class Settings(
    GoogleServiceSettings,
    DBSettings
):
    model_config = {
        "env_file": ("envs/google_services.env","envs/db.env")
    }

settings = Settings() #type: ignore