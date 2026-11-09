import { beforeEach, describe, expect, it, vi } from "vitest";

import { SendMessageError, streamMessage } from "./streamMessage";

const post = vi.fn();

vi.mock("@/services/api/client", () => ({
  api: { POST: (...args: unknown[]) => post(...args) },
}));

function streamOf(chunks: string[]): ReadableStream<Uint8Array> {
  const encoder = new TextEncoder();
  return new ReadableStream({
    start(controller) {
      for (const chunk of chunks) controller.enqueue(encoder.encode(chunk));
      controller.close();
    },
  });
}

describe("streamMessage", () => {
  beforeEach(() => post.mockReset());

  it("entrega cada evento, mesmo quebrado entre pedaços da rede", async () => {
    post.mockResolvedValue({
      data: streamOf([
        'data: {"type":"message.delta","te',
        'xt":"Ol"}\n\ndata: {"type":"message.delta","text":"á"}\n\n',
        ": ping\n\n",
      ]),
      response: { status: 200 },
    });
    const events: unknown[] = [];

    await streamMessage("c1", "Oi", {
      signal: new AbortController().signal,
      onEvent: (event) => events.push(event),
    });

    expect(events).toEqual([
      { type: "message.delta", text: "Ol" },
      { type: "message.delta", text: "á" },
    ]);
    expect(post).toHaveBeenCalledWith(
      "/api/v1/conversations/{conversationId}/messages/stream",
      expect.objectContaining({
        params: { path: { conversationId: "c1" } },
        body: { content: "Oi" },
        parseAs: "stream",
      }),
    );
  });

  it("rejeita com o status e o código quando a API recusa antes do stream", async () => {
    post.mockResolvedValue({
      error: { error: { code: "NOT_FOUND", message: "x" } },
      response: { status: 404 },
    });

    const result = streamMessage("c1", "Oi", {
      signal: new AbortController().signal,
      onEvent: vi.fn(),
    });

    await expect(result).rejects.toEqual(
      expect.objectContaining({ status: 404, code: "NOT_FOUND" }),
    );
    await expect(result).rejects.toBeInstanceOf(SendMessageError);
  });
});
