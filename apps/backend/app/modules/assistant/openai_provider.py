"""Implementação do `LLMProvider` com a Responses API da OpenAI."""

import logging
from collections.abc import AsyncIterator
from typing import Any

import anyio
import openai
from openai import AsyncOpenAI

from app.modules.assistant.llm import Completion, LLMProviderError, LLMStreamEvent, TextDelta
from app.modules.context import ModelContext

logger = logging.getLogger(__name__)


class OpenAIProvider:
    def __init__(
        self,
        client: AsyncOpenAI | None,
        model: str,
        reasoning_effort: str,
        max_output_tokens: int,
    ) -> None:
        # client None = chave não configurada; a falha só aparece ao gerar uma resposta.
        self.client = client
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.max_output_tokens = max_output_tokens

    async def stream(self, context: ModelContext) -> AsyncIterator[LLMStreamEvent]:
        if self.client is None:
            raise LLMProviderError("OpenAI API key is not configured.")
        try:
            stream = await self.client.responses.create(
                model=self.model,
                instructions=context.instructions,
                input=[{"role": m.role, "content": m.content} for m in context.messages],  # type: ignore[misc]
                reasoning={"effort": self.reasoning_effort},  # type: ignore[typeddict-item]
                max_output_tokens=self.max_output_tokens,
                # Não guardar as conversas na OpenAI (o padrão da API é guardar).
                store=False,
                stream=True,
            )
        except openai.APIError as error:
            raise LLMProviderError(f"OpenAI request failed: {type(error).__name__}") from error

        try:
            async for event in stream:
                mapped = _map_event(event)
                if mapped is not None:
                    yield mapped
                    if isinstance(mapped, Completion):
                        return
            raise LLMProviderError("OpenAI stream ended without completion.")
        except openai.APIError as error:
            raise LLMProviderError(f"OpenAI stream failed: {type(error).__name__}") from error
        finally:
            # Fecha a conexão mesmo quando o cliente desconecta (cancelamento).
            with anyio.CancelScope(shield=True):
                await stream.close()


def _map_event(event: Any) -> LLMStreamEvent | None:
    match event.type:
        case "response.output_text.delta":
            return TextDelta(text=event.delta)
        case "response.completed":
            usage = event.response.usage
            return Completion(
                model=event.response.model,
                input_tokens=usage.input_tokens if usage else None,
                output_tokens=usage.output_tokens if usage else None,
            )
        case "response.incomplete":
            details = event.response.incomplete_details
            reason = details.reason if details else "unknown"
            raise LLMProviderError(f"OpenAI response incomplete: {reason}")
        case "response.failed":
            error = event.response.error
            code = error.code if error else "unknown"
            raise LLMProviderError(f"OpenAI response failed: {code}")
        case "error":
            raise LLMProviderError(f"OpenAI stream error: {event.code}")
        case _:
            return None
