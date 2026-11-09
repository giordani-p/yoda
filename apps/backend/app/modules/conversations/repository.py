"""Acesso a dados do módulo."""

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.conversations.models import ConversationRecord, MessageRecord
from app.modules.conversations.pagination import Cursor


class ConversationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, record: ConversationRecord) -> ConversationRecord:
        self.session.add(record)
        await self.session.commit()
        await self.session.refresh(record)
        return record

    async def get_active(self, user_id: UUID, conversation_id: UUID) -> ConversationRecord | None:
        """Conversa do usuário que não foi excluída."""
        return await self.session.scalar(
            select(ConversationRecord).where(
                ConversationRecord.id == conversation_id,
                ConversationRecord.user_id == user_id,
                ConversationRecord.deleted_at.is_(None),
            )
        )

    async def list_active(
        self, user_id: UUID, cursor: Cursor | None, limit: int
    ) -> list[ConversationRecord]:
        """Até `limit` conversas, da atualizada mais recentemente para a mais antiga."""
        query = select(ConversationRecord).where(
            ConversationRecord.user_id == user_id, ConversationRecord.deleted_at.is_(None)
        )
        if cursor:
            query = query.where(
                tuple_(ConversationRecord.updated_at, ConversationRecord.id)
                < tuple_(cursor.at, cursor.id)
            )
        query = query.order_by(
            ConversationRecord.updated_at.desc(), ConversationRecord.id.desc()
        ).limit(limit)
        return list(await self.session.scalars(query))

    async def soft_delete(self, record: ConversationRecord) -> None:
        record.deleted_at = datetime.now(UTC)
        await self.session.commit()

    async def list_messages(
        self, conversation_id: UUID, cursor: Cursor | None, limit: int
    ) -> list[MessageRecord]:
        """Até `limit` mensagens, da mais recente para a mais antiga."""
        query = select(MessageRecord).where(MessageRecord.conversation_id == conversation_id)
        if cursor:
            query = query.where(
                tuple_(MessageRecord.created_at, MessageRecord.id) < tuple_(cursor.at, cursor.id)
            )
        query = query.order_by(MessageRecord.created_at.desc(), MessageRecord.id.desc()).limit(
            limit
        )
        return list(await self.session.scalars(query))
