import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ConversationList } from "./ConversationList";

const createMutate = vi.fn();
const deleteMutate = vi.fn();
const fetchNextPage = vi.fn();
let conversationsState: Record<string, unknown> = {};

vi.mock("./api", () => ({
  useConversations: () => conversationsState,
  useCreateConversation: () => ({
    mutate: createMutate,
    isPending: false,
    isError: false,
  }),
  useDeleteConversation: () => ({
    mutate: deleteMutate,
    isPending: false,
    isError: false,
  }),
}));

const page = (items: { id: string; title: string | null }[]) => ({
  items: items.map((item) => ({
    ...item,
    createdAt: "2026-01-01T00:00:00Z",
    updatedAt: "2026-01-01T00:00:00Z",
  })),
  nextCursor: null,
});

function renderList() {
  render(
    <MemoryRouter>
      <ConversationList />
    </MemoryRouter>,
  );
}

describe("ConversationList", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    conversationsState = {
      isPending: false,
      isError: false,
      isSuccess: true,
      hasNextPage: false,
      fetchNextPage,
      data: {
        pages: [
          page([
            { id: "c1", title: "Plano de viagem" },
            { id: "c2", title: null },
          ]),
        ],
      },
    };
  });

  it("lista as conversas, usando título padrão quando não há título", () => {
    renderList();

    expect(
      screen.getByRole("link", { name: "Plano de viagem" }),
    ).toHaveAttribute("href", "/c/c1");
    expect(screen.getByRole("link", { name: "Nova conversa" })).toHaveAttribute(
      "href",
      "/c/c2",
    );
  });

  it("cria uma conversa", () => {
    renderList();

    fireEvent.click(screen.getByRole("button", { name: "Nova conversa" }));

    expect(createMutate).toHaveBeenCalled();
  });

  it("exclui uma conversa após confirmação", () => {
    vi.spyOn(window, "confirm").mockReturnValue(true);
    renderList();

    fireEvent.click(
      screen.getByRole("button", { name: "Excluir Plano de viagem" }),
    );

    expect(deleteMutate).toHaveBeenCalledWith("c1", expect.anything());
  });

  it("não exclui sem confirmação", () => {
    vi.spyOn(window, "confirm").mockReturnValue(false);
    renderList();

    fireEvent.click(
      screen.getByRole("button", { name: "Excluir Plano de viagem" }),
    );

    expect(deleteMutate).not.toHaveBeenCalled();
  });

  it("carrega mais conversas quando há próxima página", () => {
    conversationsState = { ...conversationsState, hasNextPage: true };
    renderList();

    fireEvent.click(screen.getByRole("button", { name: "Carregar mais" }));

    expect(fetchNextPage).toHaveBeenCalled();
  });

  it("mostra estado vazio", () => {
    conversationsState = { ...conversationsState, data: { pages: [page([])] } };
    renderList();

    expect(screen.getByText("Nenhuma conversa ainda.")).toBeInTheDocument();
  });
});
