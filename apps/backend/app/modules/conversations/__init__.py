"""Módulo `conversations`: conversas, mensagens, histórico e paginação.

Interface pública: somente o que é exportado aqui pode ser usado fora do módulo.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.conversations.repository import ConversationRepository
from app.modules.conversations.router import router
from app.modules.conversations.schemas import Message
from app.modules.conversations.service import (
    ConversationNotFoundError,
    ConversationService,
    StoredMessage,
)


def build_conversation_service(session: AsyncSession) -> ConversationService:
    return ConversationService(ConversationRepository(session))


__all__ = [
    "ConversationNotFoundError",
    "ConversationService",
    "Message",
    "StoredMessage",
    "build_conversation_service",
    "router",
]
