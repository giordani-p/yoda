import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { MessageContent } from "./MessageContent";

describe("MessageContent", () => {
  it("renderiza Markdown nas respostas do assistente", () => {
    render(
      <MessageContent
        role="assistant"
        content={"**importante**\n\n- item\n\n[site](https://example.com)"}
      />,
    );

    expect(screen.getByText("importante").tagName).toBe("STRONG");
    expect(screen.getByRole("listitem")).toHaveTextContent("item");
    expect(screen.getByRole("link", { name: "site" })).toHaveAttribute(
      "target",
      "_blank",
    );
  });

  it("não executa HTML bruto", () => {
    const { container } = render(
      <MessageContent
        role="assistant"
        content={'<img src="x" onerror="alert(1)">'}
      />,
    );

    expect(container.querySelector("img")).toBeNull();
  });

  it("mostra a mensagem do usuário como texto", () => {
    render(<MessageContent role="user" content="**sem formatação**" />);

    expect(screen.getByText("**sem formatação**")).toBeInTheDocument();
  });
});
