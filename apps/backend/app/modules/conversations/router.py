"""Rotas HTTP do módulo. O `name` de cada rota vira o operationId do contrato."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ErrorResponse
from app.modules.conversations.repository import ConversationRepository
from app.modules.conversations.schemas import (
    Conversation,
    ConversationPage,
    Message,
    MessagePage,
)
from app.modules.conversations.service import ConversationService
from app.shared.database import get_db
from app.shared.security import CurrentUserId

router = APIRouter(prefix="/conversations", tags=["conversations"])

UNAUTHENTICATED = {
    401: {"model": ErrorResponse, "description": "Missing, invalid or expired session."}
}
NOT_FOUND = {404: {"model": ErrorResponse, "description": "Conversation not found."}}
VALIDATION_ERROR = {422: {"model": ErrorResponse, "description": "Invalid request."}}


def get_service(db: Annotated[AsyncSession, Depends(get_db)]) -> ConversationService:
    return ConversationService(ConversationRepository(db))


Service = Annotated[ConversationService, Depends(get_service)]
ConversationId = Annotated[UUID, Path(alias="conversationId")]
PageCursor = Annotated[str | None, Query()]
PageLimit = Annotated[int, Query(ge=1, le=100)]


@router.post(
    "",
    name="createConversation",
    summary="Create an empty conversation",
    status_code=status.HTTP_201_CREATED,
    responses=UNAUTHENTICATED,
)
async def create_conversation(user_id: CurrentUserId, service: Service) -> Conversation:
    return Conversation.model_validate(await service.create_conversation(user_id))


@router.get(
    "",
    name="listConversations",
    summary="List conversations, most recently updated first",
    responses={**UNAUTHENTICATED, **VALIDATION_ERROR},
)
async def list_conversations(
    user_id: CurrentUserId, service: Service, cursor: PageCursor = None, limit: PageLimit = 20
) -> ConversationPage:
    page = await service.list_conversations(user_id, cursor, limit)
    return ConversationPage(
        items=[Conversation.model_validate(c) for c in page.items], next_cursor=page.next_cursor
    )


@router.get(
    "/{conversationId}",
    name="getConversation",
    summary="Get a conversation",
    responses={**UNAUTHENTICATED, **NOT_FOUND, **VALIDATION_ERROR},
)
async def get_conversation(
    conversation_id: ConversationId, user_id: CurrentUserId, service: Service
) -> Conversation:
    return Conversation.model_validate(await service.get_conversation(user_id, conversation_id))


@router.delete(
    "/{conversationId}",
    name="deleteConversation",
    summary="Delete a conversation",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={**UNAUTHENTICATED, **NOT_FOUND, **VALIDATION_ERROR},
)
async def delete_conversation(
    conversation_id: ConversationId, user_id: CurrentUserId, service: Service
) -> None:
    await service.delete_conversation(user_id, conversation_id)


@router.get(
    "/{conversationId}/messages",
    name="listMessages",
    summary="List messages of a conversation",
    responses={**UNAUTHENTICATED, **NOT_FOUND, **VALIDATION_ERROR},
)
async def list_messages(
    conversation_id: ConversationId,
    user_id: CurrentUserId,
    service: Service,
    cursor: PageCursor = None,
    limit: PageLimit = 20,
) -> MessagePage:
    page = await service.list_messages(user_id, conversation_id, cursor, limit)
    return MessagePage(
        items=[Message.model_validate(m) for m in page.items], next_cursor=page.next_cursor
    )
