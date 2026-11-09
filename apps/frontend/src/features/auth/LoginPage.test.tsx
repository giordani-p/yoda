import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { LoginPage } from "./LoginPage";

const mutate = vi.fn();
let loginState: Record<string, unknown> = {};

vi.mock("./api", () => ({
  useCurrentUser: () => ({ data: null }),
  useLogin: () => ({ mutate, isPending: false, ...loginState }),
}));

function renderPage() {
  render(
    <MemoryRouter>
      <LoginPage />
    </MemoryRouter>,
  );
}

describe("LoginPage", () => {
  beforeEach(() => {
    mutate.mockReset();
    loginState = { isError: false, error: null };
  });

  it("envia e-mail e senha", () => {
    renderPage();

    fireEvent.change(screen.getByLabelText("E-mail"), {
      target: { value: "ana@example.com" },
    });
    fireEvent.change(screen.getByLabelText("Senha"), {
      target: { value: "segredo-123" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Entrar" }));

    expect(mutate).toHaveBeenCalledWith(
      { email: "ana@example.com", password: "segredo-123" },
      expect.anything(),
    );
  });

  it("mostra mensagem de credenciais inválidas", () => {
    loginState = {
      isError: true,
      error: { error: { code: "INVALID_CREDENTIALS", message: "x" } },
    };

    renderPage();

    expect(screen.getByRole("alert")).toHaveTextContent(
      "E-mail ou senha inválidos.",
    );
  });

  it("mostra mensagem genérica para outros erros", () => {
    loginState = {
      isError: true,
      error: { error: { code: "INTERNAL", message: "x" } },
    };

    renderPage();

    expect(screen.getByRole("alert")).toHaveTextContent(
      "Não foi possível entrar. Tente novamente.",
    );
  });
});
