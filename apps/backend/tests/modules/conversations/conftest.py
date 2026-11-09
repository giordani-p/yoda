from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from httpx2 import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.conversations.models import MessageRecord
from app.modules.users.models import UserRecord
from app.shared.security import SESSION_COOKIE_NAME, create_session_token

BASE_TIME = datetime(2026, 1, 1, tzinfo=UTC)


async def _create_user(db_session: AsyncSession, email: str) -> UserRecord:
    user = UserRecord(email=email, name=email.split("@")[0], password_hash="not-used")
    db_session.add(user)
    await db_session.commit()
    return user


def login_as(client: AsyncClient, user: UserRecord) -> None:
    client.cookies.set(SESSION_COOKIE_NAME, create_session_token(user.id))


@pytest.fixture
async def owner(db_session: AsyncSession) -> UserRecord:
    return await _create_user(db_session, "owner@example.com")


@pytest.fixture
async def other_user(db_session: AsyncSession) -> UserRecord:
    return await _create_user(db_session, "other@example.com")


@pytest.fixture
def owner_client(client: AsyncClient, owner: UserRecord) -> AsyncClient:
    login_as(client, owner)
    return client


async def add_messages(db_session: AsyncSession, conversation_id: UUID, count: int) -> None:
    """Cria `count` mensagens alternando usuário e assistente, um minuto entre cada uma."""
    for index in range(count):
        db_session.add(
            MessageRecord(
                conversation_id=conversation_id,
                role="user" if index % 2 == 0 else "assistant",
                content=f"mensagem {index}",
                created_at=BASE_TIME + timedelta(minutes=index),
            )
        )
    await db_session.commit()
