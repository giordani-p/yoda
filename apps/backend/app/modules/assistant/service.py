"""Orquestração de uma interação: contexto → modelo (streaming) → gravação da resposta."""

import logging
import time
from collections.abc import AsyncIterator
from contextlib import aclosing
from uuid import UUID

from app.core.exceptions import ErrorDetail
from app.modules.assistant.llm import Completion, LLMProvider, LLMProviderError, TextDelta
from app.modules.assistant.schemas import (
    MessageCompletedEvent,
    MessageDeltaEvent,
    MessageErrorEvent,
    MessageStreamEvent,
    UserMessageEvent,
)
from app.modules.context import ContextProvider
from app.modules.conversations import (
    ConversationNotFoundError,
    ConversationService,
    Message,
    StoredMessage,
)

logger = logging.getLogger(__name__)


def _error_event(code: str, message: str) -> MessageStreamEvent:
    return MessageStreamEvent(
        MessageErrorEvent(type="message.error", error=ErrorDetail(code=code, message=message))
    )


class AssistantService:
    def __init__(
        self,
        conversations: ConversationService,
        context: ContextProvider,
        llm: LLMProvider,
    ) -> None:
        self.conversations = conversations
        self.context = context
        self.llm = llm

    async def accept_user_message(
        self, user_id: UUID, conversation_id: UUID, content: str
    ) -> StoredMessage:
        return await self.conversations.add_user_message(user_id, conversation_id, content)

    async def stream_reply(
        self, user_id: UUID, conversation_id: UUID, user_message: StoredMessage
    ) -> AsyncIterator[MessageStreamEvent]:
        """Eventos SSE da resposta. A resposta só é gravada quando concluída.

        Em falha, emite `message.error`. Se o cliente desconectar, o gerador é cancelado e nada
        é gravado (a mensagem do usuário já foi salva antes).
        """
        yield MessageStreamEvent(
            UserMessageEvent(type="message.user", message=Message.model_validate(user_message))
        )

        started = time.perf_counter()
        first_delta_at: float | None = None
        parts: list[str] = []
        completion: Completion | None = None
        try:
            context = await self.context.build_context(conversation_id, user_id)
            async with aclosing(self.llm.stream(context)) as stream:
                async for item in stream:
                    if isinstance(item, TextDelta):
                        first_delta_at = first_delta_at or time.perf_counter()
                        parts.append(item.text)
                        yield MessageStreamEvent(
                            MessageDeltaEvent(type="message.delta", text=item.text)
                        )
                    else:
                        completion = item
            if completion is None:
                raise LLMProviderError("Provider stream ended without completion.")
            reply = await self.conversations.add_assistant_message(
                user_id,
                conversation_id,
                "".join(parts),
                model=completion.model,
                input_tokens=completion.input_tokens,
                output_tokens=completion.output_tokens,
            )
        except LLMProviderError as error:
            logger.warning(
                "Assistant reply failed: conversation=%s error=%s", conversation_id, error
            )
            yield _error_event("LLM_PROVIDER_ERROR", "The assistant could not generate a reply.")
            return
        except ConversationNotFoundError:
            # Conversa excluída durante a geração.
            yield _error_event("NOT_FOUND", f"Conversation {conversation_id} not found.")
            return
        except Exception:
            logger.exception(
                "Unexpected error in assistant reply: conversation=%s", conversation_id
            )
            yield _error_event("INTERNAL_ERROR", "Unexpected error while generating the reply.")
            return

        total_ms = (time.perf_counter() - started) * 1000
        ttft_ms = (first_delta_at - started) * 1000 if first_delta_at else None
        # Sem conteúdo das mensagens no log (privacidade).
        logger.info(
            "Assistant reply completed: conversation=%s model=%s instructions=%s "
            "ttft_ms=%s total_ms=%.0f input_tokens=%s output_tokens=%s",
            conversation_id,
            completion.model,
            context.instructions_version,
            f"{ttft_ms:.0f}" if ttft_ms is not None else None,
            total_ms,
            completion.input_tokens,
            completion.output_tokens,
        )
        yield MessageStreamEvent(
            MessageCompletedEvent(type="message.completed", message=Message.model_validate(reply))
        )
