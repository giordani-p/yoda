import { EventSourceParserStream } from "eventsource-parser/stream";

import { api, type Schemas } from "@/services/api/client";

export type MessageStreamEvent = Schemas["MessageStreamEvent"];

/** Falha antes de o stream começar (401, 404, 422): a resposta veio como JSON. */
export class SendMessageError extends Error {
  constructor(
    readonly status: number,
    readonly code: string | undefined,
  ) {
    super(`Send message failed with status ${status}`);
  }
}

/**
 * Envia a mensagem e chama `onEvent` para cada evento SSE da resposta.
 * Resolve quando o stream termina; rejeita com `SendMessageError` antes do stream ou com
 * `AbortError` quando `signal` é abortado.
 */
export async function streamMessage(
  conversationId: string,
  content: string,
  options: {
    signal: AbortSignal;
    onEvent: (event: MessageStreamEvent) => void;
  },
): Promise<void> {
  const { data, error, response } = await api.POST(
    "/api/v1/conversations/{conversationId}/messages/stream",
    {
      params: { path: { conversationId } },
      body: { content },
      parseAs: "stream",
      signal: options.signal,
    },
  );
  if (error || !data) {
    const code = (error as Schemas["ErrorResponse"] | undefined)?.error.code;
    throw new SendMessageError(response.status, code);
  }

  const reader = data
    .pipeThrough(new TextDecoderStream())
    .pipeThrough(new EventSourceParserStream())
    .getReader();
  for (;;) {
    const { done, value } = await reader.read();
    if (done) return;
    options.onEvent(JSON.parse(value.data) as MessageStreamEvent);
  }
}
