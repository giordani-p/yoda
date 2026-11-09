"""Acesso a dados do módulo."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.example.models import ExampleRecord


class ExampleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(self) -> list[ExampleRecord]:
        return list(await self.session.scalars(select(ExampleRecord).order_by(ExampleRecord.id)))

    async def get(self, example_id: int) -> ExampleRecord | None:
        return await self.session.get(ExampleRecord, example_id)

    async def add(self, record: ExampleRecord) -> ExampleRecord:
        self.session.add(record)
        await self.session.commit()
        await self.session.refresh(record)
        return record
