import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ConversationView } from "./ConversationView";

const fetchNextPage = vi.fn();
let conversationState: Record<string, unknown> = {};
let historyState: Record<string, unknown> = {};

vi.mock("./api", () => ({
  useConversation: () => conversationState,
  useMessages: () => historyState,
}));

function renderView() {
  render(
    <MemoryRouter initialEntries={["/c/c1"]}>
      <Routes>
        <Route path="/c/:conversationId" element={<ConversationView />} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("ConversationView", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    conversationState = {
      isPending: false,
      isError: false,
      data: {
        id: "c1",
        title: "Plano de viagem",
        createdAt: "2026-01-01T00:00:00Z",
        updatedAt: "2026-01-01T00:00:00Z",
      },
    };
    historyState = {
      isPending: false,
      isError: false,
      isSuccess: true,
      hasNextPage: false,
      fetchNextPage,
      messages: [
        { id: "m1", role: "user", content: "Olá", createdAt: "" },
        { id: "m2", role: "assistant", content: "Oi!", createdAt: "" },
      ],
    };
  });

  it("mostra o título e as mensagens em ordem", () => {
    renderView();

    expect(
      screen.getByRole("heading", { name: "Plano de viagem" }),
    ).toBeInTheDocument();
    const items = screen.getAllByRole("listitem");
    expect(items[0]).toHaveTextContent("VocêOlá");
    expect(items[1]).toHaveTextContent("YodaOi!");
  });

  it("carrega mensagens anteriores quando há mais páginas", () => {
    historyState = { ...historyState, hasNextPage: true };
    renderView();

    fireEvent.click(
      screen.getByRole("button", { name: "Carregar mensagens anteriores" }),
    );

    expect(fetchNextPage).toHaveBeenCalled();
  });

  it("mostra conversa não encontrada", () => {
    conversationState = {
      isPending: false,
      isError: true,
      error: { error: { code: "NOT_FOUND", message: "x" } },
    };

    renderView();

    expect(screen.getByRole("alert")).toHaveTextContent(
      "Conversa não encontrada.",
    );
  });

  it("mostra estado vazio", () => {
    historyState = { ...historyState, messages: [] };

    renderView();

    expect(screen.getByText("Nenhuma mensagem ainda.")).toBeInTheDocument();
  });
});
