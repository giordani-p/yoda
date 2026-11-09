import {
  useInfiniteQuery,
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import { api, type Schemas } from "@/services/api/client";

export const conversationsKey = ["conversations"];

const conversationKey = (conversationId: string) => [
  ...conversationsKey,
  conversationId,
];

const messagesKey = (conversationId: string) => [
  ...conversationKey(conversationId),
  "messages",
];

export type ApiError = Schemas["ErrorResponse"];

/** Conversas do usuário, da atualizada mais recentemente para a mais antiga. */
export function useConversations() {
  return useInfiniteQuery<Schemas["ConversationPage"], ApiError>({
    queryKey: conversationsKey,
    initialPageParam: undefined as string | undefined,
    queryFn: async ({ pageParam }) => {
      const { data, error } = await api.GET("/api/v1/conversations", {
        params: { query: { cursor: pageParam as string | undefined } },
      });
      if (error) throw error;
      return data;
    },
    getNextPageParam: (lastPage) => lastPage.nextCursor ?? undefined,
  });
}

export function useConversation(conversationId: string) {
  return useQuery<Schemas["Conversation"], ApiError>({
    queryKey: conversationKey(conversationId),
    queryFn: async () => {
      const { data, error } = await api.GET(
        "/api/v1/conversations/{conversationId}",
        { params: { path: { conversationId } } },
      );
      if (error) throw error;
      return data;
    },
    retry: false,
  });
}

/**
 * Histórico da conversa. A primeira página traz as mensagens mais recentes; as seguintes,
 * as anteriores. `messages` já vem em ordem cronológica.
 */
export function useMessages(conversationId: string) {
  const query = useInfiniteQuery<Schemas["MessagePage"], ApiError>({
    queryKey: messagesKey(conversationId),
    initialPageParam: undefined as string | undefined,
    queryFn: async ({ pageParam }) => {
      const { data, error } = await api.GET(
        "/api/v1/conversations/{conversationId}/messages",
        {
          params: {
            path: { conversationId },
            query: { cursor: pageParam as string | undefined },
          },
        },
      );
      if (error) throw error;
      return data;
    },
    getNextPageParam: (lastPage) => lastPage.nextCursor ?? undefined,
    retry: false,
  });
  const messages =
    query.data?.pages
      .slice()
      .reverse()
      .flatMap((page) => page.items) ?? [];
  return { ...query, messages };
}

export function useCreateConversation() {
  const queryClient = useQueryClient();
  return useMutation<Schemas["Conversation"], ApiError>({
    mutationFn: async () => {
      const { data, error } = await api.POST("/api/v1/conversations");
      if (error) throw error;
      return data;
    },
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: conversationsKey }),
  });
}

export function useDeleteConversation() {
  const queryClient = useQueryClient();
  return useMutation<void, ApiError, string>({
    mutationFn: async (conversationId) => {
      const { error } = await api.DELETE(
        "/api/v1/conversations/{conversationId}",
        { params: { path: { conversationId } } },
      );
      if (error) throw error;
    },
    onSuccess: (_, conversationId) => {
      queryClient.removeQueries({ queryKey: conversationKey(conversationId) });
      return queryClient.invalidateQueries({
        queryKey: conversationsKey,
        exact: true,
      });
    },
  });
}
