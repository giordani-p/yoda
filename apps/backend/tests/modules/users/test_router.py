from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
import pytest
from httpx2 import AsyncClient

from app.core.config import get_settings
from app.modules.users.models import UserRecord
from app.shared.security import SESSION_COOKIE_NAME, create_session_token
from tests.modules.users.conftest import EMAIL, PASSWORD

pytestmark = pytest.mark.anyio

LOGIN = "/api/v1/auth/login"
LOGOUT = "/api/v1/auth/logout"
ME = "/api/v1/users/me"


async def test_login_sets_http_only_session_cookie(client: AsyncClient, user: UserRecord) -> None:
    response = await client.post(LOGIN, json={"email": EMAIL, "password": PASSWORD})

    assert response.status_code == 204
    assert response.content == b""
    cookie = response.headers["set-cookie"]
    assert cookie.startswith(f"{SESSION_COOKIE_NAME}=")
    assert "HttpOnly" in cookie
    assert "SameSite=lax" in cookie


async def test_login_ignores_email_case_and_spaces(client: AsyncClient, user: UserRecord) -> None:
    response = await client.post(LOGIN, json={"email": "  ANA@Example.com ", "password": PASSWORD})

    assert response.status_code == 204


@pytest.mark.parametrize(
    "credentials",
    [
        {"email": EMAIL, "password": "wrong-password"},
        {"email": "nobody@example.com", "password": PASSWORD},
    ],
)
async def test_login_with_invalid_credentials_returns_401(
    client: AsyncClient, user: UserRecord, credentials: dict[str, str]
) -> None:
    response = await client.post(LOGIN, json=credentials)

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"
    assert "set-cookie" not in response.headers


async def test_login_with_invalid_payload_returns_422(client: AsyncClient) -> None:
    response = await client.post(LOGIN, json={"email": ""})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


async def test_current_user_after_login(client: AsyncClient, user: UserRecord) -> None:
    await client.post(LOGIN, json={"email": EMAIL, "password": PASSWORD})

    response = await client.get(ME)

    assert response.status_code == 200
    assert response.json() == {"id": str(user.id), "email": EMAIL, "name": "Ana"}


async def test_current_user_without_session_returns_401(client: AsyncClient) -> None:
    response = await client.get(ME)

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHENTICATED"


@pytest.mark.parametrize(
    "token",
    [
        "not-a-jwt",
        jwt.encode({"sub": str(uuid4()), "exp": datetime.now(UTC)}, "x" * 32, algorithm="HS256"),
    ],
    ids=["malformed", "wrong-signature"],
)
async def test_current_user_with_invalid_token_returns_401(client: AsyncClient, token: str) -> None:
    client.cookies.set(SESSION_COOKIE_NAME, token)

    response = await client.get(ME)

    assert response.status_code == 401


async def test_current_user_with_expired_token_returns_401(
    client: AsyncClient, user: UserRecord
) -> None:
    expired = jwt.encode(
        {"sub": str(user.id), "exp": datetime.now(UTC) - timedelta(seconds=1)},
        get_settings().auth_secret_key,
        algorithm="HS256",
    )
    client.cookies.set(SESSION_COOKIE_NAME, expired)

    response = await client.get(ME)

    assert response.status_code == 401


async def test_current_user_that_no_longer_exists_returns_401(client: AsyncClient) -> None:
    client.cookies.set(SESSION_COOKIE_NAME, create_session_token(uuid4()))

    response = await client.get(ME)

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHENTICATED"


async def test_logout_clears_session(client: AsyncClient, user: UserRecord) -> None:
    await client.post(LOGIN, json={"email": EMAIL, "password": PASSWORD})

    response = await client.post(LOGOUT)

    assert response.status_code == 204
    assert f'{SESSION_COOKIE_NAME}=""' in response.headers["set-cookie"]
    assert (await client.get(ME)).status_code == 401
