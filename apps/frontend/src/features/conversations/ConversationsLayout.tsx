import { Outlet } from "react-router";

import { ConversationList } from "./ConversationList";

export function ConversationsLayout() {
  return (
    <div className="conversations-layout">
      <ConversationList />
      <Outlet />
    </div>
  );
}

export function NoConversationSelected() {
  return <p>Selecione uma conversa ou crie uma nova.</p>;
}
