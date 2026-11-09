"""Agrega os routers dos módulos. Não contém rotas próprias."""

from fastapi import APIRouter

from app.modules import assistant, conversations, users

api_router = APIRouter()
api_router.include_router(users.router)
api_router.include_router(conversations.router)
api_router.include_router(assistant.router)
