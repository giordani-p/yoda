"""Regras de negócio do módulo: cadastro de usuários e verificação de credenciais."""

from functools import cache
from uuid import UUID

from fastapi import status
from pwdlib import PasswordHash
from starlette.concurrency import run_in_threadpool

from app.core.exceptions import AppError
from app.modules.users.models import UserRecord
from app.modules.users.repository import UserRepository

MIN_PASSWORD_LENGTH = 8

_password_hash = PasswordHash.recommended()


class InvalidCredentialsError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "INVALID_CREDENTIALS"


class EmailAlreadyRegisteredError(AppError):
    status_code = status.HTTP_409_CONFLICT
    code = "EMAIL_ALREADY_REGISTERED"


class InvalidUserDataError(AppError):
    code = "INVALID_USER_DATA"


@cache
def _dummy_hash() -> str:
    """Hash usado quando o e-mail não existe, para o tempo de resposta não revelar isso."""
    return _password_hash.hash("dummy-password-for-constant-time-checks")


def normalize_email(email: str) -> str:
    return email.strip().lower()


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    async def get_user(self, user_id: UUID) -> UserRecord | None:
        return await self.repository.get(user_id)

    async def authenticate(self, email: str, password: str) -> UserRecord:
        user = await self.repository.get_by_email(normalize_email(email))
        stored_hash = user.password_hash if user else _dummy_hash()
        # O hash argon2 é custoso em CPU; roda fora do event loop.
        valid = await run_in_threadpool(_password_hash.verify, password, stored_hash)
        if user is None or not valid:
            raise InvalidCredentialsError("Invalid email or password.")
        return user

    async def create_user(self, email: str, name: str, password: str) -> UserRecord:
        email = normalize_email(email)
        name = name.strip()
        if "@" not in email or not name:
            raise InvalidUserDataError("A valid email and a name are required.")
        if len(password) < MIN_PASSWORD_LENGTH:
            raise InvalidUserDataError(
                f"Password must have at least {MIN_PASSWORD_LENGTH} characters."
            )
        if await self.repository.get_by_email(email):
            raise EmailAlreadyRegisteredError(f"Email {email} is already registered.")
        password_hash = await run_in_threadpool(_password_hash.hash, password)
        return await self.repository.add(
            UserRecord(email=email, name=name, password_hash=password_hash)
        )
