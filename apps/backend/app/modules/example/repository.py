"""Acesso a dados do módulo."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.example.models import ExampleRecord


class ExampleRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list(self) -> list[ExampleRecord]:
        return list(self.session.scalars(select(ExampleRecord).order_by(ExampleRecord.id)))

    def get(self, example_id: int) -> ExampleRecord | None:
        return self.session.get(ExampleRecord, example_id)

    def add(self, record: ExampleRecord) -> ExampleRecord:
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record
