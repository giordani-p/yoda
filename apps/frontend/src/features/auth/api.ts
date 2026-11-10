import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api, type Schemas } from "@/services/api/client";

export const currentUserKey = ["currentUser"];

/** Usuário autenticado, ou `null` quando não há sessão válida. */
export function useCurrentUser() {
  return useQuery({
    queryKey: currentUserKey,
    queryFn: async () => {
      const { data, error, response } = await api.GET("/api/v1/users/me");
      if (response.status === 401) return null;
      if (error) throw error;
      return data;
    },
    retry: false,
    staleTime: Infinity,
  });
}

export function useLogin() {
  const queryClient = useQueryClient();
  return useMutation<void, Schemas["ErrorResponse"], Schemas["LoginRequest"]>({
    mutationFn: async (body) => {
      const { error } = await api.POST("/api/v1/auth/login", { body });
      if (error) throw error;
    },
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: currentUserKey }),
  });
}

export function useLogout() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      await api.POST("/api/v1/auth/logout");
    },
    // Descarta todos os dados em cache do usuário que saiu.
    onSuccess: () => {
      queryClient.clear();
      queryClient.setQueryData(currentUserKey, null);
    },
  });
}
