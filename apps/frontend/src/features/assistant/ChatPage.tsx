import { useEffect, useRef } from "react";
import { useParams } from "react-router";

import { UNTITLED_CONVERSATION } from "@/features/conversations/ConversationList";
import { MessageContent } from "@/features/conversations/MessageContent";
import { MessageItem, MessageList } from "@/features/conversations/MessageList";
import { useConversation, useMessages } from "@/features/conversations/api";

import { Composer } from "./Composer";
import { useSendMessage, type LiveTurn } from "./useSendMessage";

const TURN_NOTICES: Partial<Record<LiveTurn["status"], string>> = {
  failed: "Não foi possível gerar a resposta.",
  interrupted: "Resposta interrompida.",
};

export function ChatPage() {
  const { conversationId = "" } = useParams();
  // A `key` recria o chat ao trocar de conversa, zerando a resposta ao vivo.
  return <Chat key={conversationId} conversationId={conversationId} />;
}

function Chat({ conversationId }: { conversationId: string }) {
  const conversation = useConversation(conversationId);
  const history = useMessages(conversationId);
  const { turn, send, stop, isStreaming } = useSendMessage(conversationId);
  const endRef = useRef<HTMLDivElement>(null);

  const lastMessageId = history.messages.at(-1)?.id;
  useEffect(() => {
    endRef.current?.scrollIntoView?.({ block: "end" });
  }, [lastMessageId, turn?.assistantText]);

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

  // A mensagem do usuário aparece ao vivo até chegar no histórico recarregado.
  const pendingUserMessage =
    turn?.userMessage &&
    !history.messages.some((message) => message.id === turn.userMessage?.id)
      ? turn.userMessage
      : undefined;
  const showAssistantTurn = turn && turn.status !== "rejected";
  const notice = turn && TURN_NOTICES[turn.status];

  return (
    <section className="chat">
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
      {history.isSuccess && history.messages.length === 0 && !turn && (
        <p>Nenhuma mensagem ainda.</p>
      )}

      <MessageList messages={history.messages}>
        {pendingUserMessage && (
          <MessageItem role="user">
            <MessageContent role="user" content={pendingUserMessage.content} />
          </MessageItem>
        )}
        {showAssistantTurn && (
          <MessageItem role="assistant">
            {turn.assistantText ? (
              <MessageContent role="assistant" content={turn.assistantText} />
            ) : (
              turn.status === "streaming" && <p>Yoda está escrevendo...</p>
            )}
            {notice && <p role="alert">{notice}</p>}
          </MessageItem>
        )}
      </MessageList>
      <div ref={endRef} />

      {turn?.status === "rejected" && (
        <p role="alert">Não foi possível enviar a mensagem.</p>
      )}
      <Composer
        isStreaming={isStreaming}
        onSend={async (content) => (await send(content)) !== "rejected"}
        onStop={stop}
      />
    </section>
  );
}
