"""Fixtures compartilhadas. Os testes usam um banco Postgres de teste (TEST_DATABASE_URL).

O banco é criado se não existir e o schema é recriado uma vez por execução. Cada teste roda dentro
de uma transação desfeita ao final, então os commits feitos pelo código não vazam entre testes.
Os testes são assíncronos e rodam com o plugin pytest do anyio (marque com `pytest.mark.anyio`).
"""

from collections.abc import AsyncIterator

import pytest
from httpx2 import ASGITransport, AsyncClient
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import make_url, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from app.main import app
from app.modules.users.models import UserRecord
from app.shared.database import Base, get_db
from tests.helpers import create_user, login_as


class DatabaseTestSettings(BaseSettings):
    # Mesmo .env da aplicação, relativo a apps/backend (onde o pytest roda).
    model_config = SettingsConfigDict(env_file="../../.env", extra="ignore")

    test_database_url: str = "postgresql+psycopg://yoda:change-me@localhost:5432/yoda_test"


async def _create_database_if_missing(url: str) -> None:
    target = make_url(url)
    admin = create_async_engine(target.set(database="postgres"), isolation_level="AUTOCOMMIT")
    async with admin.connect() as connection:
        exists = await connection.scalar(
            text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": target.database}
        )
        if not exists:
            await connection.execute(text(f'CREATE DATABASE "{target.database}"'))
    await admin.dispose()


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session")
async def engine() -> AsyncIterator[AsyncEngine]:
    url = DatabaseTestSettings().test_database_url
    await _create_database_if_missing(url)
    engine = create_async_engine(url)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(
            bind=connection, join_transaction_mode="create_savepoint", expire_on_commit=False
        )
        yield session
        await session.close()
        await transaction.rollback()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncIterator[AsyncClient]:
    app.dependency_overrides[get_db] = lambda: db_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
async def owner(db_session: AsyncSession) -> UserRecord:
    return await create_user(db_session, "owner@example.com")


@pytest.fixture
async def other_user(db_session: AsyncSession) -> UserRecord:
    return await create_user(db_session, "other@example.com")


@pytest.fixture
def owner_client(client: AsyncClient, owner: UserRecord) -> AsyncClient:
    """Client autenticado como `owner`."""
    login_as(client, owner)
    return client
