"""Regras de negócio do módulo: ciclo de vida das conversas e leitura do histórico."""

from uuid import UUID

from app.core.exceptions import NotFoundError
from app.modules.conversations.models import ConversationRecord, MessageRecord
from app.modules.conversations.pagination import Cursor, Page
from app.modules.conversations.repository import ConversationRepository


class ConversationNotFoundError(NotFoundError):
    def __init__(self, conversation_id: UUID) -> None:
        super().__init__(f"Conversation {conversation_id} not found.")


class ConversationService:
    def __init__(self, repository: ConversationRepository) -> None:
        self.repository = repository

    async def create_conversation(self, user_id: UUID) -> ConversationRecord:
        return await self.repository.add(ConversationRecord(user_id=user_id))

    async def get_conversation(self, user_id: UUID, conversation_id: UUID) -> ConversationRecord:
        """Conversa ativa do usuário. Excluída ou de outro usuário responde como inexistente."""
        conversation = await self.repository.get_active(user_id, conversation_id)
        if conversation is None:
            raise ConversationNotFoundError(conversation_id)
        return conversation

    async def list_conversations(
        self, user_id: UUID, cursor: str | None, limit: int
    ) -> Page[ConversationRecord]:
        # Busca um item a mais para saber se existe próxima página.
        records = await self.repository.list_active(user_id, _decode(cursor), limit + 1)
        items = records[:limit]
        has_more = len(records) > limit
        next_cursor = Cursor(items[-1].updated_at, items[-1].id).encode() if has_more else None
        return Page(items=items, next_cursor=next_cursor)

    async def delete_conversation(self, user_id: UUID, conversation_id: UUID) -> None:
        conversation = await self.get_conversation(user_id, conversation_id)
        await self.repository.soft_delete(conversation)

    async def list_messages(
        self, user_id: UUID, conversation_id: UUID, cursor: str | None, limit: int
    ) -> Page[MessageRecord]:
        """Página com as mensagens mais recentes, em ordem cronológica.

        O `next_cursor` aponta para as mensagens anteriores à mais antiga da página.
        """
        await self.get_conversation(user_id, conversation_id)
        records = await self.repository.list_messages(conversation_id, _decode(cursor), limit + 1)
        newest_first = records[:limit]
        has_more = len(records) > limit
        oldest = newest_first[-1] if newest_first else None
        next_cursor = Cursor(oldest.created_at, oldest.id).encode() if has_more and oldest else None
        return Page(items=list(reversed(newest_first)), next_cursor=next_cursor)


def _decode(cursor: str | None) -> Cursor | None:
    return Cursor.decode(cursor) if cursor else None
