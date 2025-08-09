from sqlalchemy.ext.asyncio import async_sessionmaker
from app.database.postgres.setup_postgres import engine

class DatabaseDependencies():
    async_session_factory = async_sessionmaker(bind=engine)

    @staticmethod
    async def get_session():
        async with DatabaseDependencies.async_session_factory() as session:
            yield session

class DependencyContainer(
    DatabaseDependencies
):
    pass