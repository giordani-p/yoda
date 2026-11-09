"""Rotas HTTP do módulo. O `name` de cada rota vira o operationId do contrato."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ErrorResponse
from app.modules.example.repository import ExampleRepository
from app.modules.example.schemas import Example, ExampleCreate, ExampleList
from app.modules.example.service import ExampleService
from app.shared.database import get_db

router = APIRouter(prefix="/examples", tags=["examples"])

VALIDATION_ERROR = {422: {"model": ErrorResponse, "description": "Invalid request."}}
NOT_FOUND = {404: {"model": ErrorResponse, "description": "Example not found."}}


def get_service(db: Annotated[AsyncSession, Depends(get_db)]) -> ExampleService:
    return ExampleService(ExampleRepository(db))


Service = Annotated[ExampleService, Depends(get_service)]


@router.get("", name="listExamples", summary="List examples")
async def list_examples(service: Service) -> ExampleList:
    examples = await service.list_examples()
    return ExampleList(items=[Example.model_validate(e) for e in examples])


@router.post(
    "",
    name="createExample",
    summary="Create an example",
    status_code=status.HTTP_201_CREATED,
    responses=VALIDATION_ERROR,
)
async def create_example(data: ExampleCreate, service: Service) -> Example:
    return Example.model_validate(await service.create_example(data.name, data.description))


@router.get(
    "/{exampleId}",
    name="getExample",
    summary="Get an example by id",
    responses={**NOT_FOUND, **VALIDATION_ERROR},
)
async def get_example(
    example_id: Annotated[int, Path(alias="exampleId")], service: Service
) -> Example:
    return Example.model_validate(await service.get_example(example_id))
