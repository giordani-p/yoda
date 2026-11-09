"""Rotas HTTP do módulo. O `name` de cada rota vira o operationId do contrato."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ErrorResponse, UnauthenticatedError
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import LoginRequest, User
from app.modules.users.service import UserService
from app.shared.database import get_db
from app.shared.security import CurrentUserId, clear_session_cookie, set_session_cookie

router = APIRouter()

VALIDATION_ERROR = {422: {"model": ErrorResponse, "description": "Invalid request."}}
UNAUTHENTICATED = {
    401: {"model": ErrorResponse, "description": "Missing, invalid or expired session."}
}


def get_service(db: Annotated[AsyncSession, Depends(get_db)]) -> UserService:
    return UserService(UserRepository(db))


Service = Annotated[UserService, Depends(get_service)]


@router.post(
    "/auth/login",
    name="login",
    tags=["auth"],
    summary="Authenticate and start a session",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid email or password."},
        **VALIDATION_ERROR,
    },
)
async def login(data: LoginRequest, response: Response, service: Service) -> None:
    user = await service.authenticate(data.email, data.password)
    set_session_cookie(response, user.id)


@router.post(
    "/auth/logout",
    name="logout",
    tags=["auth"],
    summary="End the session",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(response: Response) -> None:
    clear_session_cookie(response)


@router.get(
    "/users/me",
    name="getCurrentUser",
    tags=["users"],
    summary="Get the authenticated user",
    responses=UNAUTHENTICATED,
)
async def get_current_user(user_id: CurrentUserId, service: Service) -> User:
    user = await service.get_user(user_id)
    if user is None:
        # Token válido de um usuário que não existe mais.
        raise UnauthenticatedError("Authentication required.")
    return User.model_validate(user)
