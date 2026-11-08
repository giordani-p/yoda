"""Ponto de entrada da aplicação FastAPI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import setup_logging


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
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.get("/health", include_in_schema=False)
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
