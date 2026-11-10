import { NavLink, useNavigate, useParams } from "react-router";

import {
  useConversations,
  useCreateConversation,
  useDeleteConversation,
} from "./api";

export const UNTITLED_CONVERSATION = "Nova conversa";

export function ConversationList() {
  const conversations = useConversations();
  const createConversation = useCreateConversation();
  const deleteConversation = useDeleteConversation();
  const navigate = useNavigate();
  const { conversationId: openConversationId } = useParams();

  function handleCreate() {
    createConversation.mutate(undefined, {
      onSuccess: (conversation) => navigate(`/c/${conversation.id}`),
    });
  }

  function handleDelete(conversationId: string) {
    if (!window.confirm("Excluir esta conversa?")) return;
    deleteConversation.mutate(conversationId, {
      onSuccess: () => {
        if (conversationId === openConversationId) navigate("/");
      },
    });
  }

  const items = conversations.data?.pages.flatMap((page) => page.items) ?? [];

  return (
    <nav className="conversation-list" aria-label="Conversas">
      <button
        type="button"
        onClick={handleCreate}
        disabled={createConversation.isPending}
      >
        Nova conversa
      </button>
      {createConversation.isError && (
        <p role="alert">Não foi possível criar a conversa.</p>
      )}
      {deleteConversation.isError && (
        <p role="alert">Não foi possível excluir a conversa.</p>
      )}

      {conversations.isPending && <p>Carregando...</p>}
      {conversations.isError && (
        <p role="alert">Não foi possível carregar as conversas.</p>
      )}
      {conversations.isSuccess && items.length === 0 && (
        <p>Nenhuma conversa ainda.</p>
      )}

      <ul>
        {items.map((conversation) => (
          <li key={conversation.id}>
            <NavLink to={`/c/${conversation.id}`}>
              {conversation.title ?? UNTITLED_CONVERSATION}
            </NavLink>
            <button
              type="button"
              aria-label={`Excluir ${conversation.title ?? UNTITLED_CONVERSATION}`}
              onClick={() => handleDelete(conversation.id)}
              disabled={deleteConversation.isPending}
            >
              Excluir
            </button>
          </li>
        ))}
      </ul>

      {conversations.hasNextPage && (
        <button
          type="button"
          onClick={() => conversations.fetchNextPage()}
          disabled={conversations.isFetchingNextPage}
        >
          Carregar mais
        </button>
      )}
    </nav>
  );
}
