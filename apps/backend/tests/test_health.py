from typing import Any

import pytest
from httpx2 import AsyncClient
from sqlalchemy.exc import OperationalError

from app.main import app
from app.shared.database import get_db

pytestmark = pytest.mark.anyio


class _UnavailableSession:
    """Sessão falsa que simula o banco fora do ar."""

    async def execute(self, *_: Any, **__: Any) -> None:
        raise OperationalError("SELECT 1", {}, Exception("connection refused"))


async def test_health_returns_ok_when_database_is_available(client: AsyncClient) -> None:
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_health_returns_503_when_database_is_unavailable(client: AsyncClient) -> None:
    app.dependency_overrides[get_db] = lambda: _UnavailableSession()

    response = await client.get("/health")

    assert response.status_code == 503
    assert response.json() == {"status": "unavailable"}
