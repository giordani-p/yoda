import type { ReactNode } from "react";

import type { Schemas } from "@/services/api/client";

import { MessageContent } from "./MessageContent";

export const ROLE_LABELS = { user: "Você", assistant: "Yoda" } as const;

export function MessageItem({
  role,
  children,
}: {
  role: Schemas["Message"]["role"];
  children: ReactNode;
}) {
  return (
    <li className={`message message-${role}`}>
      <strong>{ROLE_LABELS[role]}</strong>
      {children}
    </li>
  );
}

/** Mensagens persistidas, em ordem cronológica. `children` entra depois delas (resposta ao vivo). */
export function MessageList({
  messages,
  children,
}: {
  messages: Schemas["Message"][];
  children?: ReactNode;
}) {
  return (
    <ol className="messages">
      {messages.map((message) => (
        <MessageItem key={message.id} role={message.role}>
          <MessageContent role={message.role} content={message.content} />
        </MessageItem>
      ))}
      {children}
    </ol>
  );
}
