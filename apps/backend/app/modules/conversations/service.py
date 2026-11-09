"""Regras de negócio do módulo: ciclo de vida das conversas e leitura do histórico."""

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal
from uuid import UUID

from app.core.exceptions import NotFoundError
from app.modules.conversations.models import ConversationRecord, MessageRecord
from app.modules.conversations.pagination import Cursor, Page
from app.modules.conversations.repository import ConversationRepository

TITLE_MAX_LENGTH = 60

Role = Literal["user", "assistant"]


@dataclass(frozen=True)
class StoredMessage:
    """Mensagem persistida, como exposta a outros módulos (sem detalhes de persistência)."""

    id: UUID
    role: Role
    content: str
    created_at: datetime


def _to_stored(record: MessageRecord) -> StoredMessage:
    return StoredMessage(
        id=record.id,
        role=record.role,  # type: ignore[arg-type]
        content=record.content,
        created_at=record.created_at,
    )


def title_from_message(content: str) -> str:
    """Título da conversa: início da primeira mensagem, em uma linha, com até 60 caracteres."""
    single_line = re.sub(r"\s+", " ", content).strip()
    if len(single_line) <= TITLE_MAX_LENGTH:
        return single_line
    return single_line[: TITLE_MAX_LENGTH - 1].rstrip() + "…"


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

    async def add_user_message(
        self, user_id: UUID, conversation_id: UUID, content: str
    ) -> StoredMessage:
        """Grava a mensagem do usuário. A primeira mensagem define o título da conversa."""
        conversation = await self.get_conversation(user_id, conversation_id)
        record = await self.repository.add_message(
            conversation,
            MessageRecord(
                conversation_id=conversation_id,
                role="user",
                content=content,
                created_at=datetime.now(UTC),
            ),
            title=title_from_message(content),
        )
        return _to_stored(record)

    async def add_assistant_message(
        self,
        user_id: UUID,
        conversation_id: UUID,
        content: str,
        model: str,
        input_tokens: int | None,
        output_tokens: int | None,
    ) -> StoredMessage:
        """Grava a resposta concluída do assistente, com os metadados da geração."""
        conversation = await self.get_conversation(user_id, conversation_id)
        record = await self.repository.add_message(
            conversation,
            MessageRecord(
                conversation_id=conversation_id,
                role="assistant",
                content=content,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                created_at=datetime.now(UTC),
            ),
            title=None,
        )
        return _to_stored(record)

    async def recent_messages(
        self, user_id: UUID, conversation_id: UUID, limit: int
    ) -> list[StoredMessage]:
        """Últimas `limit` mensagens da conversa, em ordem cronológica.

        Encerra a transação de leitura ao final, pois é chamado antes da geração da resposta.
        """
        await self.get_conversation(user_id, conversation_id)
        records = await self.repository.list_messages(conversation_id, None, limit)
        messages = [_to_stored(record) for record in reversed(records)]
        await self.repository.end_read()
        return messages


def _decode(cursor: str | None) -> Cursor | None:
    return Cursor.decode(cursor) if cursor else None
