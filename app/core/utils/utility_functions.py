from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user_info_models import UserInDB

class TimeUtilityFunctions():

    @staticmethod
    def get_utc_offset_string():
        now = datetime.now().astimezone()
        offset = now.utcoffset()
        total_minutes = offset.total_seconds() // 60 #type: ignore
        sign = "+" if total_minutes >= 0 else "-"
        total_minutes = abs(int(total_minutes))
        hours, minutes = divmod(total_minutes, 60)
        return f"UTC{sign}{hours:02d}:{minutes:02d}"

class GoogleServiceUtilityFunctions():
    
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
                "refresh_token": token.get("refresh_token",None),
                "expire_in": token.get("expires_in",None)
            }

class DBUtilityFunctions():

    @staticmethod
    async def update_credenctials_to_db(session: AsyncSession, credentials: dict):
        user_id = credentials.get("user_id",None)
        email = credentials.get("email",None)
        name = credentials.get("name",None)
        access_token = credentials.get("access_token",None)
        refresh_token = credentials.get("refresh_token",None)
        expire_in = credentials.get("expire_in",None)
        
        if user_id is None or email is None or name is None or access_token is None or expire_in is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed: Missing required user details from OAuth provider."
            )
        else:
            curr_time = datetime.now(timezone.utc)
            expire_time = curr_time + timedelta(seconds=expire_in)
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
                    refresh_token=refresh_token,
                    expire_time=expire_time
                )
                session.add(new_user)
                await session.commit()
            else:
                user.access_token=access_token
                user.expire_time=expire_time
                session.add(user)
                await session.commit()

class UtilityContainer(
    GoogleServiceUtilityFunctions,
    DBUtilityFunctions,
    TimeUtilityFunctions
):
    pass