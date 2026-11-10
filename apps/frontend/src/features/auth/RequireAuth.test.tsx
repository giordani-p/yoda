import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router";
import { describe, expect, it, vi } from "vitest";

import { RequireAuth } from "./RequireAuth";

let currentUser: Record<string, unknown> = {};

vi.mock("./api", () => ({
  useCurrentUser: () => currentUser,
}));

function renderProtectedRoute() {
  render(
    <MemoryRouter initialEntries={["/"]}>
      <Routes>
        <Route path="/login" element={<p>Tela de login</p>} />
        <Route element={<RequireAuth />}>
          <Route path="/" element={<p>Área protegida</p>} />
        </Route>
      </Routes>
    </MemoryRouter>,
  );
}

describe("RequireAuth", () => {
  it("redireciona para o login sem sessão", () => {
    currentUser = { isPending: false, isError: false, data: null };

    renderProtectedRoute();

    expect(screen.getByText("Tela de login")).toBeInTheDocument();
  });

  it("mostra a rota protegida com sessão", () => {
    currentUser = {
      isPending: false,
      isError: false,
      data: { id: "1", email: "ana@example.com", name: "Ana" },
    };

    renderProtectedRoute();

    expect(screen.getByText("Área protegida")).toBeInTheDocument();
  });
});
