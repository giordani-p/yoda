from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.conversations.models import MessageRecord

BASE_TIME = datetime(2026, 1, 1, tzinfo=UTC)


async def add_messages(db_session: AsyncSession, conversation_id: UUID, count: int) -> None:
    """Cria `count` mensagens alternando usuário e assistente, um minuto entre cada uma."""
    for index in range(count):
        db_session.add(
            MessageRecord(
                conversation_id=conversation_id,
                role="user" if index % 2 == 0 else "assistant",
                content=f"mensagem {index}",
                created_at=BASE_TIME + timedelta(minutes=index),
            )
        )
    await db_session.commit()
