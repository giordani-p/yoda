"""Base declarativa compartilhada por todos os models SQLAlchemy."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
