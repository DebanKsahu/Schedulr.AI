from fastapi import FastAPI
from contextlib import asynccontextmanager
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.postgres.setup_postgres import engine, init_db, close_db
from app.api.v1.login import login_router
from app.api.v1.routes.schedule import schedule_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db(engine=engine)
    yield
    await close_db(engine=engine)

app = FastAPI(lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=settings.CLIENT_SECRET)
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)
app.include_router(login_router)
app.include_router(schedule_router)