"""Utilitários compartilhados pelos testes."""

import json
from typing import Any

from httpx2 import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import UserRecord
from app.shared.security import SESSION_COOKIE_NAME, create_session_token


async def create_user(db_session: AsyncSession, email: str) -> UserRecord:
    user = UserRecord(email=email, name=email.split("@")[0], password_hash="not-used")
    db_session.add(user)
    await db_session.commit()
    return user


def login_as(client: AsyncClient, user: UserRecord) -> None:
    client.cookies.set(SESSION_COOKIE_NAME, create_session_token(user.id))


def parse_sse(body: str) -> list[dict[str, Any]]:
    """Converte um corpo `text/event-stream` na lista de `data` (JSON) de cada evento."""
    events = []
    for block in body.strip().split("\n\n"):
        data = [line[len("data: ") :] for line in block.splitlines() if line.startswith("data: ")]
        if data:
            events.append(json.loads("\n".join(data)))
    return events
