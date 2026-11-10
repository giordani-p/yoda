import { useState, type FormEvent, type KeyboardEvent } from "react";

export const MESSAGE_MAX_LENGTH = 10_000;

/** Campo de mensagem. Enter envia; Shift+Enter quebra linha. */
export function Composer({
  isStreaming,
  onSend,
  onStop,
}: {
  isStreaming: boolean;
  /** Devolve `false` quando a mensagem não foi aceita, para restaurar o texto. */
  onSend: (content: string) => Promise<boolean>;
  onStop: () => void;
}) {
  const [content, setContent] = useState("");
  const canSend = !isStreaming && content.trim().length > 0;

  async function submit() {
    if (!canSend) return;
    const sent = content;
    setContent("");
    if (!(await onSend(sent))) setContent(sent);
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    void submit();
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void submit();
    }
  }

  return (
    <form className="composer" onSubmit={handleSubmit}>
      <label htmlFor="composer-input" className="visually-hidden">
        Mensagem
      </label>
      <textarea
        id="composer-input"
        value={content}
        onChange={(event) => setContent(event.target.value)}
        onKeyDown={handleKeyDown}
        maxLength={MESSAGE_MAX_LENGTH}
        placeholder="Escreva sua mensagem"
        rows={3}
      />
      {isStreaming ? (
        <button type="button" onClick={onStop}>
          Parar
        </button>
      ) : (
        <button type="submit" disabled={!canSend}>
          Enviar
        </button>
      )}
    </form>
  );
}
