"""Cursor opaco da paginação: codifica a posição (data, id) do último item da página."""

import base64
import json
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.core.exceptions import InvalidRequestError


@dataclass(frozen=True)
class Cursor:
    at: datetime
    id: UUID

    def encode(self) -> str:
        raw = json.dumps({"at": self.at.isoformat(), "id": str(self.id)}).encode()
        return base64.urlsafe_b64encode(raw).decode().rstrip("=")

    @classmethod
    def decode(cls, value: str) -> "Cursor":
        try:
            padded = value + "=" * (-len(value) % 4)
            data = json.loads(base64.urlsafe_b64decode(padded))
            return cls(at=datetime.fromisoformat(data["at"]), id=UUID(data["id"]))
        except (ValueError, KeyError, TypeError) as error:
            raise InvalidRequestError("Invalid cursor.") from error


@dataclass(frozen=True)
class Page[T]:
    items: list[T]
    next_cursor: str | None
