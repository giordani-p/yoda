"""Token de sessão: JWT assinado (HS256) guardado num cookie HttpOnly."""

from datetime import UTC, datetime, timedelta
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, Response
from fastapi.security import APIKeyCookie

from app.core.config import get_settings
from app.core.exceptions import UnauthenticatedError

SESSION_COOKIE_NAME = "yoda_session"
_ALGORITHM = "HS256"

# auto_error=False: a ausência do cookie vira UnauthenticatedError, com o envelope de erro padrão.
_session_cookie = APIKeyCookie(
    name=SESSION_COOKIE_NAME, scheme_name="sessionCookie", auto_error=False
)


def create_session_token(user_id: UUID) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(hours=settings.auth_token_ttl_hours),
    }
    return jwt.encode(payload, settings.auth_secret_key, algorithm=_ALGORITHM)


def _read_session_token(token: str) -> UUID | None:
    """Devolve o id do usuário de um token válido, ou None se for inválido ou expirado."""
    try:
        payload = jwt.decode(
            token,
            get_settings().auth_secret_key,
            algorithms=[_ALGORITHM],
            options={"require": ["sub", "exp"]},
        )
        return UUID(payload["sub"])
    except (jwt.InvalidTokenError, ValueError):
        return None


def set_session_cookie(response: Response, user_id: UUID) -> None:
    settings = get_settings()
    response.set_cookie(
        SESSION_COOKIE_NAME,
        create_session_token(user_id),
        max_age=settings.auth_token_ttl_hours * 3600,
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite="lax",
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(
        SESSION_COOKIE_NAME,
        httponly=True,
        secure=get_settings().auth_cookie_secure,
        samesite="lax",
        path="/",
    )


async def get_current_user_id(
    token: Annotated[str | None, Depends(_session_cookie)],
) -> UUID:
    """Dependência do FastAPI: id do usuário autenticado, ou 401 se não houver sessão válida."""
    user_id = _read_session_token(token) if token else None
    if user_id is None:
        raise UnauthenticatedError("Authentication required.")
    return user_id


CurrentUserId = Annotated[UUID, Depends(get_current_user_id)]
