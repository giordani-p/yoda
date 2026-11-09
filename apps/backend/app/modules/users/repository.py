"""Acesso a dados do módulo."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import UserRecord


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, user_id: UUID) -> UserRecord | None:
        return await self.session.get(UserRecord, user_id)

    async def get_by_email(self, email: str) -> UserRecord | None:
        return await self.session.scalar(select(UserRecord).where(UserRecord.email == email))

    async def add(self, record: UserRecord) -> UserRecord:
        self.session.add(record)
        await self.session.commit()
        await self.session.refresh(record)
        return record
