import { useParams } from "react-router";

import { UNTITLED_CONVERSATION } from "./ConversationList";
import { useConversation, useMessages } from "./api";

const ROLE_LABELS = { user: "Você", assistant: "Yoda" } as const;

export function ConversationView() {
  const { conversationId = "" } = useParams();
  const conversation = useConversation(conversationId);
  const history = useMessages(conversationId);

  if (conversation.isPending) return <p>Carregando...</p>;
  if (conversation.isError) {
    return (
      <p role="alert">
        {conversation.error.error.code === "NOT_FOUND"
          ? "Conversa não encontrada."
          : "Não foi possível carregar a conversa."}
      </p>
    );
  }

  return (
    <section className="conversation">
      <h1>{conversation.data.title ?? UNTITLED_CONVERSATION}</h1>

      {history.hasNextPage && (
        <button
          type="button"
          onClick={() => history.fetchNextPage()}
          disabled={history.isFetchingNextPage}
        >
          Carregar mensagens anteriores
        </button>
      )}

      {history.isPending && <p>Carregando mensagens...</p>}
      {history.isError && (
        <p role="alert">Não foi possível carregar as mensagens.</p>
      )}
      {history.isSuccess && history.messages.length === 0 && (
        <p>Nenhuma mensagem ainda.</p>
      )}

      <ol className="messages">
        {history.messages.map((message) => (
          <li key={message.id} className={`message message-${message.role}`}>
            <strong>{ROLE_LABELS[message.role]}</strong>
            <p>{message.content}</p>
          </li>
        ))}
      </ol>
    </section>
  );
}
