import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { act, fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router";
import { beforeEach, describe, expect, it, vi } from "vitest";

import type { MessageStreamEvent } from "./streamMessage";
import { ChatPage } from "./ChatPage";

type StreamOptions = {
  signal: AbortSignal;
  onEvent: (event: MessageStreamEvent) => void;
};

const streamMessage =
  vi.fn<
    (id: string, content: string, options: StreamOptions) => Promise<void>
  >();
let historyState: Record<string, unknown> = {};

vi.mock("./streamMessage", async (importOriginal) => ({
  ...(await importOriginal<typeof import("./streamMessage")>()),
  streamMessage: (id: string, content: string, options: StreamOptions) =>
    streamMessage(id, content, options),
}));

vi.mock("@/features/conversations/api", () => ({
  conversationsKey: ["conversations"],
  useConversation: () => ({
    isPending: false,
    isError: false,
    data: { id: "c1", title: "Plano de viagem", createdAt: "", updatedAt: "" },
  }),
  useMessages: () => historyState,
}));

const userMessage = {
  id: "m1",
  role: "user",
  content: "Olá",
  createdAt: "",
} as const;

function renderChat() {
  render(
    <QueryClientProvider client={new QueryClient()}>
      <MemoryRouter initialEntries={["/c/c1"]}>
        <Routes>
          <Route path="/c/:conversationId" element={<ChatPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

async function send(text: string) {
  fireEvent.change(screen.getByLabelText("Mensagem"), {
    target: { value: text },
  });
  await act(async () => {
    fireEvent.click(screen.getByRole("button", { name: "Enviar" }));
  });
}

describe("ChatPage", () => {
  beforeEach(() => {
    streamMessage.mockReset();
    historyState = {
      isPending: false,
      isError: false,
      isSuccess: true,
      hasNextPage: false,
      messages: [],
    };
  });

  it("mostra o histórico", () => {
    historyState = {
      ...historyState,
      messages: [
        userMessage,
        { id: "m2", role: "assistant", content: "Oi!", createdAt: "" },
      ],
    };

    renderChat();

    const items = screen.getAllByRole("listitem");
    expect(items[0]).toHaveTextContent("VocêOlá");
    expect(items[1]).toHaveTextContent("YodaOi!");
  });

  it("mostra a resposta ao vivo e o aviso quando a geração falha", async () => {
    streamMessage.mockImplementation(async (_id, _content, { onEvent }) => {
      onEvent({ type: "message.user", message: userMessage });
      onEvent({ type: "message.delta", text: "Resposta par" });
      onEvent({ type: "message.delta", text: "cial" });
      onEvent({
        type: "message.error",
        error: { code: "LLM_PROVIDER_ERROR", message: "x" },
      });
    });
    renderChat();

    await send("Olá");

    expect(streamMessage).toHaveBeenCalledWith("c1", "Olá", expect.anything());
    expect(screen.getByText("Olá")).toBeInTheDocument();
    expect(screen.getByText("Resposta parcial")).toBeInTheDocument();
    expect(screen.getByRole("alert")).toHaveTextContent(
      "Não foi possível gerar a resposta.",
    );
  });

  it("interrompe a resposta com o botão Parar", async () => {
    streamMessage.mockImplementation(
      (_id, _content, { signal, onEvent }) =>
        new Promise((_, reject) => {
          onEvent({ type: "message.delta", text: "Começo" });
          signal.addEventListener("abort", () =>
            reject(new DOMException("aborted", "AbortError")),
          );
        }),
    );
    renderChat();
    await send("Olá");

    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: "Parar" }));
    });

    expect(screen.getByText("Começo")).toBeInTheDocument();
    expect(screen.getByRole("alert")).toHaveTextContent(
      "Resposta interrompida.",
    );
    expect(screen.getByRole("button", { name: "Enviar" })).toBeInTheDocument();
  });

  it("remove a resposta ao vivo quando concluída (ela vem do histórico)", async () => {
    streamMessage.mockImplementation(async (_id, _content, { onEvent }) => {
      onEvent({ type: "message.delta", text: "Pronto" });
      onEvent({
        type: "message.completed",
        message: {
          id: "m2",
          role: "assistant",
          content: "Pronto",
          createdAt: "",
        },
      });
    });
    renderChat();

    await send("Olá");

    expect(screen.queryByText("Pronto")).not.toBeInTheDocument();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("avisa e devolve o texto quando o envio é recusado", async () => {
    const { SendMessageError } = await import("./streamMessage");
    streamMessage.mockRejectedValue(new SendMessageError(404, "NOT_FOUND"));
    renderChat();

    await send("Olá");

    expect(screen.getByRole("alert")).toHaveTextContent(
      "Não foi possível enviar a mensagem.",
    );
    expect(screen.getByLabelText("Mensagem")).toHaveValue("Olá");
  });
});
