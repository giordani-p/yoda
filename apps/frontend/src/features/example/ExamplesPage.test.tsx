import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { ExamplesPage } from "./ExamplesPage";

vi.mock("./api", () => ({
  useExamples: () => ({
    data: [
      {
        id: 1,
        name: "Primeiro",
        description: null,
        createdAt: "2026-01-01T00:00:00Z",
      },
    ],
    isPending: false,
    isError: false,
  }),
  useCreateExample: () => ({
    mutate: vi.fn(),
    isPending: false,
    isError: false,
  }),
}));

describe("ExamplesPage", () => {
  it("lista os exemplos retornados pela API", () => {
    render(<ExamplesPage />);

    expect(screen.getByText("Primeiro")).toBeInTheDocument();
  });
});
