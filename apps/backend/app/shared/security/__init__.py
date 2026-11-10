"""Identificação do usuário autenticado na requisição.

Emite e verifica o token de sessão guardado no cookie HttpOnly `yoda_session`, sem acessar o
banco (ADR 0004). Regras de negócio de usuários pertencem ao módulo `users`.
"""

from app.shared.security.session import (
    SESSION_COOKIE_NAME,
    CurrentUserId,
    clear_session_cookie,
    create_session_token,
    get_current_user_id,
    set_session_cookie,
)

__all__ = [
    "SESSION_COOKIE_NAME",
    "CurrentUserId",
    "clear_session_cookie",
    "create_session_token",
    "get_current_user_id",
    "set_session_cookie",
]
