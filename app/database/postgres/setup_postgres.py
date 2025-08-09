from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from app.core.config import settings
from sqlmodel import SQLModel

engine = create_async_engine(
    url = settings.DB_URL,
    echo = True,
    pool_size = 5,
    max_overflow = 10,
    pool_timeout = 30
)

async def init_db(engine: AsyncEngine):
    async with engine.begin() as async_engine:
        await async_engine.run_sync(SQLModel.metadata.create_all)

async def close_db(engine: AsyncEngine):
    await engine.dispose()