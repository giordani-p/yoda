import { act, fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { Composer } from "./Composer";

function setup(isStreaming = false, accepted = true) {
  const onSend = vi.fn().mockResolvedValue(accepted);
  const onStop = vi.fn();
  render(
    <Composer isStreaming={isStreaming} onSend={onSend} onStop={onStop} />,
  );
  return { onSend, onStop, input: screen.getByLabelText("Mensagem") };
}

describe("Composer", () => {
  it("envia com Enter e limpa o campo", async () => {
    const { onSend, input } = setup();

    fireEvent.change(input, { target: { value: "Olá" } });
    await act(async () => {
      fireEvent.keyDown(input, { key: "Enter" });
    });

    expect(onSend).toHaveBeenCalledWith("Olá");
    expect(input).toHaveValue("");
  });

  it("Shift+Enter não envia", () => {
    const { onSend, input } = setup();

    fireEvent.change(input, { target: { value: "Olá" } });
    fireEvent.keyDown(input, { key: "Enter", shiftKey: true });

    expect(onSend).not.toHaveBeenCalled();
  });

  it("não envia mensagem em branco", () => {
    const { onSend, input } = setup();

    fireEvent.change(input, { target: { value: "   " } });
    fireEvent.keyDown(input, { key: "Enter" });

    expect(onSend).not.toHaveBeenCalled();
    expect(screen.getByRole("button", { name: "Enviar" })).toBeDisabled();
  });

  it("restaura o texto quando a mensagem é recusada", async () => {
    const { input } = setup(false, false);

    fireEvent.change(input, { target: { value: "Olá" } });
    await act(async () => {
      fireEvent.keyDown(input, { key: "Enter" });
    });

    expect(input).toHaveValue("Olá");
  });

  it("mostra Parar durante a resposta", () => {
    const { onStop } = setup(true);

    fireEvent.click(screen.getByRole("button", { name: "Parar" }));

    expect(onStop).toHaveBeenCalled();
    expect(
      screen.queryByRole("button", { name: "Enviar" }),
    ).not.toBeInTheDocument();
  });
});
