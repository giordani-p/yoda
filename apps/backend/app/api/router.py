"""Agrega os routers dos módulos. Não contém rotas próprias."""

from fastapi import APIRouter

from app.modules import example

api_router = APIRouter()
api_router.include_router(example.router)
