import { Navigate, Outlet } from "react-router";

import { useCurrentUser } from "./api";

/** Protege as rotas filhas: sem sessão válida, redireciona para o login. */
export function RequireAuth() {
  const currentUser = useCurrentUser();

  if (currentUser.isPending) return <p>Carregando...</p>;
  if (currentUser.isError) {
    return <p role="alert">Não foi possível verificar sua sessão.</p>;
  }
  if (!currentUser.data) return <Navigate to="/login" replace />;

  return <Outlet />;
}
