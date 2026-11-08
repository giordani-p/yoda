"""Ambiente do Alembic: usa a URL das configurações e o metadata de todos os módulos."""

import importlib
import importlib.util
import logging
import pkgutil

from alembic import context
from sqlalchemy import engine_from_config, pool

import app.modules
from app.core.config import get_settings
from app.shared.database import Base

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")

# Importa o models.py de todos os módulos. Sem isso, o autogenerate não enxerga as tabelas
# de um módulo esquecido e gera uma migration que as apaga.
for module in pkgutil.iter_modules(app.modules.__path__):
    models_path = f"app.modules.{module.name}.models"
    if importlib.util.find_spec(models_path):
        importlib.import_module(models_path)

config = context.config
config.set_main_option("sqlalchemy.url", get_settings().database_url)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(url=config.get_main_option("sqlalchemy.url"), target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    engine = engine_from_config(
        config.get_section(config.config_ini_section, {}), poolclass=pool.NullPool
    )
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
