from types import SimpleNamespace
from typing import Any

import httpx2
import openai
import pytest

from app.modules.assistant.llm import Completion, LLMProviderError, TextDelta
from app.modules.assistant.openai_provider import OpenAIProvider
from app.modules.context import ContextMessage, ModelContext

pytestmark = pytest.mark.anyio

CONTEXT = ModelContext(
    instructions="Seja útil.",
    instructions_version="v1",
    messages=[ContextMessage(role="user", content="Oi"), ContextMessage("assistant", "Olá")],
)


def _delta(text: str) -> SimpleNamespace:
    return SimpleNamespace(type="response.output_text.delta", delta=text)


def _completed() -> SimpleNamespace:
    usage = SimpleNamespace(input_tokens=12, output_tokens=3)
    return SimpleNamespace(
        type="response.completed", response=SimpleNamespace(model="gpt-test", usage=usage)
    )


class FakeStream:
    def __init__(self, events: list[Any]) -> None:
        self.events = events
        self.closed = False

    def __aiter__(self) -> "FakeStream":
        self._iterator = iter(self.events)
        return self

    async def __anext__(self) -> Any:
        try:
            event = next(self._iterator)
        except StopIteration:
            raise StopAsyncIteration from None
        if isinstance(event, Exception):
            raise event
        return event

    async def close(self) -> None:
        self.closed = True


class FakeResponses:
    def __init__(self, stream: FakeStream | Exception) -> None:
        self.stream = stream
        self.kwargs: dict[str, Any] = {}

    async def create(self, **kwargs: Any) -> FakeStream:
        self.kwargs = kwargs
        if isinstance(self.stream, Exception):
            raise self.stream
        return self.stream


def _provider(stream: FakeStream | Exception) -> tuple[OpenAIProvider, FakeResponses]:
    responses = FakeResponses(stream)
    client = SimpleNamespace(responses=responses)
    provider = OpenAIProvider(
        client,  # type: ignore[arg-type]
        model="gpt-test",
        reasoning_effort="low",
        max_output_tokens=100,
    )
    return provider, responses


async def _collect(provider: OpenAIProvider) -> list[Any]:
    return [event async for event in provider.stream(CONTEXT)]


def _connection_error() -> openai.APIConnectionError:
    return openai.APIConnectionError(request=httpx2.Request("POST", "https://api.openai.com"))


async def test_maps_deltas_and_completion() -> None:
    stream = FakeStream(
        [SimpleNamespace(type="response.created"), _delta("Ol"), _delta("á"), _completed()]
    )
    provider, _ = _provider(stream)

    events = await _collect(provider)

    assert events == [
        TextDelta("Ol"),
        TextDelta("á"),
        Completion(model="gpt-test", input_tokens=12, output_tokens=3),
    ]
    assert stream.closed


async def test_sends_context_without_storing_at_openai() -> None:
    provider, responses = _provider(FakeStream([_completed()]))

    await _collect(provider)

    assert responses.kwargs == {
        "model": "gpt-test",
        "instructions": "Seja útil.",
        "input": [{"role": "user", "content": "Oi"}, {"role": "assistant", "content": "Olá"}],
        "reasoning": {"effort": "low"},
        "max_output_tokens": 100,
        "store": False,
        "stream": True,
    }


@pytest.mark.parametrize(
    "final_event",
    [
        SimpleNamespace(
            type="response.failed",
            response=SimpleNamespace(error=SimpleNamespace(code="server_error")),
        ),
        SimpleNamespace(
            type="response.incomplete",
            response=SimpleNamespace(
                incomplete_details=SimpleNamespace(reason="max_output_tokens")
            ),
        ),
        SimpleNamespace(type="error", code="rate_limit_exceeded"),
    ],
    ids=["failed", "incomplete", "error"],
)
async def test_failure_events_raise_provider_error(final_event: SimpleNamespace) -> None:
    stream = FakeStream([_delta("parcial"), final_event])
    provider, _ = _provider(stream)

    with pytest.raises(LLMProviderError):
        await _collect(provider)
    assert stream.closed


async def test_stream_without_completion_raises() -> None:
    provider, _ = _provider(FakeStream([_delta("parcial")]))

    with pytest.raises(LLMProviderError, match="without completion"):
        await _collect(provider)


async def test_api_errors_become_provider_errors() -> None:
    provider, _ = _provider(_connection_error())
    with pytest.raises(LLMProviderError):
        await _collect(provider)

    stream = FakeStream([_delta("a"), _connection_error()])
    provider, _ = _provider(stream)
    with pytest.raises(LLMProviderError):
        await _collect(provider)
    assert stream.closed


async def test_missing_api_key_raises() -> None:
    provider = OpenAIProvider(None, model="gpt-test", reasoning_effort="low", max_output_tokens=1)

    with pytest.raises(LLMProviderError, match="not configured"):
        await _collect(provider)
