import {
  MutationCache,
  QueryCache,
  QueryClient,
  QueryClientProvider,
} from "@tanstack/react-query";
import { useState, type ReactNode } from "react";

import { currentUserKey } from "@/features/auth/api";

function isUnauthenticated(error: unknown): boolean {
  return (
    typeof error === "object" &&
    error !== null &&
    "error" in error &&
    (error as { error?: { code?: string } }).error?.code === "UNAUTHENTICATED"
  );
}

function createQueryClient(): QueryClient {
  // Sessão expirada em qualquer chamada: marca o usuário como deslogado, e a guarda de rota
  // redireciona para o login.
  const handleError = (error: unknown) => {
    if (isUnauthenticated(error))
      queryClient.setQueryData(currentUserKey, null);
  };
  const queryClient = new QueryClient({
    queryCache: new QueryCache({ onError: handleError }),
    mutationCache: new MutationCache({ onError: handleError }),
  });
  return queryClient;
}

export function AppProviders({ children }: { children: ReactNode }) {
  const [queryClient] = useState(createQueryClient);
  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}
