from os import access
from typing import Any

from fastapi import HTTPException, status
from app.core.config import Settings
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user_info_models import UserInDB


class GoogleServiceUtilityFunctions():

    @staticmethod
    def create_client_config(settings: Settings):
        return {
            "web": {
                "client_id": settings.CLIENT_ID,
                "project_id": settings.PROJECT_ID,
                "auth_uri": settings.AUTH_URL,
                "token_uri": settings.TOKEN_URL,
                "auth_provider_x509_cert_url": settings.AUTH_PROVIDER_X509_CERT_URL,
                "client_secret": settings.CLIENT_SECRET,
                "redirect_uris": settings.REDIRECT_URLS
            }
        }
    
    @staticmethod
    def create_credentials(token: Any | None):
        if token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed: No token received from OAuth provider."
            )
        else:
            user_info = token.get("userinfo",None)
            if user_info is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication failed: No user information found in token."
                )
            return {
                "user_id": user_info["sub"],
                "email": user_info["email"],
                "name": user_info["name"],
                "access_token": token.get("access_token",None),
                "refresh_token": token.get("refresh_token",None)
            }

class DBUtilityFunctions():

    @staticmethod
    async def update_credenctials_to_db(session: AsyncSession, credentials: dict):
        user_id = credentials.get("user_id",None)
        email = credentials.get("email",None)
        name = credentials.get("name",None)
        access_token = credentials.get("access_token",None)
        refresh_token = credentials.get("refresh_token",None)
        if user_id is None or email is None or name is None or access_token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed: Missing required user details from OAuth provider."
            )
        else:
            user = await session.get(UserInDB,user_id)
            if user is None:
                if refresh_token is None:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Missing refresh token from OAuth provider. Please ensure the correct scopes are requested."
                    )
                new_user = UserInDB(
                    user_id=user_id,
                    email=email,
                    name=name,
                    access_token=access_token,
                    refresh_token=refresh_token
                )
                session.add(new_user)
                await session.commit()
            else:
                user.access_token=access_token
                session.add(user)
                await session.commit()

class UtilityContainer(
    GoogleServiceUtilityFunctions,
    DBUtilityFunctions
):
    pass