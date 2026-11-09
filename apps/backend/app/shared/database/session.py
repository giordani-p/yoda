"""Engine e sessão assíncronas do banco de dados."""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

# O driver psycopg 3 atende tanto o engine assíncrono (aplicação) quanto o síncrono (Alembic).
engine = create_async_engine(get_settings().database_url, pool_pre_ping=True)
SessionLocal = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


async def get_db() -> AsyncIterator[AsyncSession]:
    """Dependência do FastAPI: abre uma sessão por request e a fecha ao final."""
    async with SessionLocal() as session:
        yield session
