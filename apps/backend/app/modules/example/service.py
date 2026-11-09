"""Regras de negócio do módulo."""

from app.core.exceptions import NotFoundError
from app.modules.example.models import ExampleRecord
from app.modules.example.repository import ExampleRepository


class ExampleService:
    def __init__(self, repository: ExampleRepository) -> None:
        self.repository = repository

    async def list_examples(self) -> list[ExampleRecord]:
        return await self.repository.list()

    async def get_example(self, example_id: int) -> ExampleRecord:
        record = await self.repository.get(example_id)
        if record is None:
            raise NotFoundError(f"Example {example_id} not found.")
        return record

    async def create_example(self, name: str, description: str | None) -> ExampleRecord:
        return await self.repository.add(ExampleRecord(name=name, description=description))
