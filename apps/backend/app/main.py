"""Ponto de entrada da aplicação FastAPI."""

import logging
from typing import Annotated

from fastapi import Depends, FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging
from app.shared.database import get_db

logger = logging.getLogger(__name__)


def _operation_id(route: APIRoute) -> str:
    """Usa o `name` da rota como operationId, igual ao definido no contrato."""
    return route.name


def create_app() -> FastAPI:
    settings = get_settings()
    setup_logging(settings.app_debug)

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        generate_unique_id_function=_operation_id,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        # Necessário para o navegador enviar o cookie de sessão a partir do frontend.
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.get("/health", include_in_schema=False)
    async def health(db: Annotated[AsyncSession, Depends(get_db)]) -> JSONResponse:
        """Verifica se a aplicação está no ar e consegue falar com o banco."""
        try:
            await db.execute(text("SELECT 1"))
        except SQLAlchemyError:
            logger.warning("Health check failed: database unavailable", exc_info=True)
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={"status": "unavailable"},
            )
        return JSONResponse(content={"status": "ok"})

    return app


app = create_app()
