"""Regras de negócio do módulo."""

from app.core.exceptions import NotFoundError
from app.modules.example.models import ExampleRecord
from app.modules.example.repository import ExampleRepository
from app.modules.example.schemas import ExampleCreate


class ExampleService:
    def __init__(self, repository: ExampleRepository) -> None:
        self.repository = repository

    def list_examples(self) -> list[ExampleRecord]:
        return self.repository.list()

    def get_example(self, example_id: int) -> ExampleRecord:
        record = self.repository.get(example_id)
        if record is None:
            raise NotFoundError(f"Example {example_id} not found.")
        return record

    def create_example(self, data: ExampleCreate) -> ExampleRecord:
        return self.repository.add(ExampleRecord(name=data.name, description=data.description))
