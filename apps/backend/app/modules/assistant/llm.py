"""Interface do LLM Gateway: o que o assistente precisa de um provedor de modelo.

Reflete o caso de uso real (resposta por streaming). Nenhum outro ponto do código chama o
provedor diretamente.
"""

from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Protocol

from app.modules.context import ModelContext


@dataclass(frozen=True)
class TextDelta:
    text: str


@dataclass(frozen=True)
class Completion:
    model: str
    input_tokens: int | None
    output_tokens: int | None


LLMStreamEvent = TextDelta | Completion


class LLMProviderError(Exception):
    """Falha do provedor: indisponível, erro da API, resposta incompleta ou não configurado."""


class LLMProvider(Protocol):
    def stream(self, context: ModelContext) -> AsyncIterator[LLMStreamEvent]:
        """Gera a resposta em fragmentos (`TextDelta`) e termina com um `Completion`.

        Levanta `LLMProviderError` em caso de falha.
        """
        ...
