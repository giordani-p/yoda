"""Rotas HTTP do módulo. O `name` de cada rota vira o operationId do contrato."""

from collections.abc import AsyncIterable
from functools import lru_cache
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Path
from fastapi.sse import EventSourceResponse
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import ErrorResponse
from app.modules.assistant.llm import LLMProvider
from app.modules.assistant.openai_provider import OpenAIProvider
from app.modules.assistant.schemas import MessageStreamEvent, SendMessageRequest
from app.modules.assistant.service import AssistantService
from app.modules.context import ConversationContextProvider
from app.modules.conversations import StoredMessage, build_conversation_service
from app.shared.database import get_db
from app.shared.security import CurrentUserId

router = APIRouter(prefix="/conversations", tags=["assistant"])


@lru_cache
def _default_llm_provider() -> OpenAIProvider:
    settings = get_settings()
    client = (
        AsyncOpenAI(api_key=settings.openai_api_key, timeout=settings.openai_timeout_seconds)
        if settings.openai_api_key
        else None
    )
    return OpenAIProvider(
        client,
        model=settings.openai_model,
        reasoning_effort=settings.openai_reasoning_effort,
        max_output_tokens=settings.openai_max_output_tokens,
    )


def get_llm_provider() -> LLMProvider:
    """Dependência do FastAPI; os testes a substituem por um provedor falso."""
    return _default_llm_provider()


def get_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    llm: Annotated[LLMProvider, Depends(get_llm_provider)],
) -> AssistantService:
    conversations = build_conversation_service(db)
    context = ConversationContextProvider(conversations, get_settings().context_recent_messages)
    return AssistantService(conversations, context, llm)


Service = Annotated[AssistantService, Depends(get_service)]
ConversationId = Annotated[UUID, Path(alias="conversationId")]


async def accept_user_message(
    conversation_id: ConversationId,
    data: SendMessageRequest,
    user_id: CurrentUserId,
    service: Service,
) -> StoredMessage:
    """Valida e grava a mensagem antes de o stream abrir: erros aqui são respostas JSON."""
    return await service.accept_user_message(user_id, conversation_id, data.content)


@router.post(
    "/{conversationId}/messages/stream",
    name="sendMessage",
    summary="Send a message and stream the assistant reply (SSE)",
    response_class=EventSourceResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Missing, invalid or expired session."},
        404: {"model": ErrorResponse, "description": "Conversation not found."},
        422: {"model": ErrorResponse, "description": "Invalid request."},
    },
)
async def send_message(
    conversation_id: ConversationId,
    user_id: CurrentUserId,
    service: Service,
    user_message: Annotated[StoredMessage, Depends(accept_user_message)],
) -> AsyncIterable[MessageStreamEvent]:
    async for event in service.stream_reply(user_id, conversation_id, user_message):
        yield event
