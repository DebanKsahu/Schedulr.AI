
from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.utils.dependency import DependencyContainer
from app.core.utils.response_model import APIResponse
from app.core.utils.utility_functions import UtilityContainer

login_router = APIRouter(
    prefix="/auth/google/v1",
    tags=["User Login"]
)

oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.CLIENT_ID,
    client_secret=settings.CLIENT_SECRET,
    server_metadata_url=settings.SERVER_METADATA_URL,
    client_kwargs={
        "scope": (" ").join(settings.SCOPES)
    }
)

@login_router.get("/login")
async def login(request: Request):
    redirect_url = request.url_for("callback")
    if oauth.google is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=APIResponse.unsuccessful_response(
                message="Google OAuth client is not configured. Please contact the server administrator."
            )
        )
    else:
        return await oauth.google.authorize_redirect(request, redirect_url, access_type="offline", prompt="consent")

@login_router.get("/callback", response_model=APIResponse)
async def callback(request: Request, background_task: BackgroundTasks, session: AsyncSession = Depends(DependencyContainer.get_session)):
        if oauth.google is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=APIResponse.unsuccessful_response(
                    message="Google OAuth client is not configured. Please contact the server administrator."
                )
            )
        else:
            token = await oauth.google.authorize_access_token(request)
            credentials_dict = UtilityContainer.create_credentials(token=token)
            background_task.add_task(UtilityContainer.update_credenctials_to_db,session,credentials_dict)
            return APIResponse.successful_response(
                message="Your credentials successfully retrieved",
                data=credentials_dict
            )