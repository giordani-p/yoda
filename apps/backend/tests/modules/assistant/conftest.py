from collections.abc import AsyncIterator, Iterator

import pytest

from app.main import app
from app.modules.assistant.llm import Completion, LLMProviderError, LLMStreamEvent, TextDelta
from app.modules.assistant.router import get_llm_provider
from app.modules.context import ModelContext


class FakeLLMProvider:
    """Provedor de teste: devolve fragmentos fixos e registra o contexto recebido."""

    def __init__(self, deltas: tuple[str, ...] = ("Olá", "!"), fail_at: int | None = None):
        self.deltas = deltas
        # Índice do fragmento em que a geração falha (len(deltas) = falha antes de concluir).
        self.fail_at = fail_at
        self.contexts: list[ModelContext] = []
        self.closed = False

    async def stream(self, context: ModelContext) -> AsyncIterator[LLMStreamEvent]:
        self.contexts.append(context)
        try:
            for index, text in enumerate(self.deltas):
                if index == self.fail_at:
                    raise LLMProviderError("fake failure")
                yield TextDelta(text)
            if self.fail_at == len(self.deltas):
                raise LLMProviderError("fake failure")
            yield Completion(model="fake-model", input_tokens=10, output_tokens=5)
        finally:
            self.closed = True


@pytest.fixture
def llm() -> FakeLLMProvider:
    return FakeLLMProvider()


@pytest.fixture(autouse=True)
def _use_fake_llm(llm: FakeLLMProvider) -> Iterator[None]:
    app.dependency_overrides[get_llm_provider] = lambda: llm
    yield
    app.dependency_overrides.pop(get_llm_provider, None)
