from sqlalchemy.ext.asyncio import async_sessionmaker
from app.database.postgres.setup_postgres import engine
from fastapi.security import OAuth2PasswordBearer

class DatabaseDependencies():
    async_session_factory = async_sessionmaker(bind=engine)

    @staticmethod
    async def get_session():
        async with DatabaseDependencies.async_session_factory() as session:
            yield session

class AuthDependencies():
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/google/v1/callback")

class DependencyContainer(
    DatabaseDependencies,
    AuthDependencies
):
    pass