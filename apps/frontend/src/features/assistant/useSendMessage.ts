import { useQueryClient } from "@tanstack/react-query";
import { useCallback, useEffect, useRef, useState } from "react";

import { currentUserKey } from "@/features/auth/api";
import { conversationsKey } from "@/features/conversations/api";
import type { Schemas } from "@/services/api/client";

import { SendMessageError, streamMessage } from "./streamMessage";

export type TurnStatus =
  "streaming" | "completed" | "failed" | "interrupted" | "rejected";

/** Interação em andamento: a resposta ao vivo, antes de entrar no histórico persistido. */
export type LiveTurn = {
  userMessage?: Schemas["Message"];
  assistantText: string;
  status: TurnStatus;
};

export function useSendMessage(conversationId: string) {
  const queryClient = useQueryClient();
  const [turn, setTurn] = useState<LiveTurn | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  // Ao sair da tela (ou trocar de conversa), interrompe a resposta em andamento.
  useEffect(() => () => abortRef.current?.abort(), []);

  const send = useCallback(
    async (content: string): Promise<TurnStatus> => {
      const controller = new AbortController();
      abortRef.current = controller;
      setTurn({ assistantText: "", status: "streaming" });

      let status: TurnStatus = "failed";
      try {
        await streamMessage(conversationId, content, {
          signal: controller.signal,
          onEvent: (event) => {
            switch (event.type) {
              case "message.user":
                setTurn(
                  (current) =>
                    current && { ...current, userMessage: event.message },
                );
                break;
              case "message.delta":
                setTurn(
                  (current) =>
                    current && {
                      ...current,
                      assistantText: current.assistantText + event.text,
                    },
                );
                break;
              case "message.completed":
                status = "completed";
                break;
              case "message.error":
                status = "failed";
                break;
            }
          },
        });
      } catch (error) {
        if (controller.signal.aborted) {
          status = "interrupted";
        } else if (error instanceof SendMessageError) {
          status = "rejected";
          if (error.status === 401)
            queryClient.setQueryData(currentUserKey, null);
        }
      }

      // O histórico, o título e a ordem da lista vêm do servidor.
      await queryClient.invalidateQueries({ queryKey: conversationsKey });
      // Concluída: a resposta já está no histórico. Senão, o parcial fica visível com o aviso.
      setTurn((current) =>
        status === "completed" ? null : current && { ...current, status },
      );
      return status;
    },
    [conversationId, queryClient],
  );

  const stop = useCallback(() => abortRef.current?.abort(), []);

  return { turn, send, stop, isStreaming: turn?.status === "streaming" };
}
