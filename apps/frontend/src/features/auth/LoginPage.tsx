import { useState, type FormEvent } from "react";
import { Navigate, useNavigate } from "react-router";

import { useCurrentUser, useLogin } from "./api";

export function LoginPage() {
  const currentUser = useCurrentUser();
  const login = useLogin();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  if (currentUser.data) return <Navigate to="/" replace />;

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    login.mutate(
      { email, password },
      { onSuccess: () => navigate("/", { replace: true }) },
    );
  }

  const invalidCredentials = login.error?.error.code === "INVALID_CREDENTIALS";

  return (
    <main className="login">
      <h1>Yoda</h1>
      <form onSubmit={handleSubmit}>
        <label htmlFor="login-email">E-mail</label>
        <input
          id="login-email"
          type="email"
          autoComplete="username"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          required
        />

        <label htmlFor="login-password">Senha</label>
        <input
          id="login-password"
          type="password"
          autoComplete="current-password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          required
        />

        <button type="submit" disabled={login.isPending}>
          {login.isPending ? "Entrando..." : "Entrar"}
        </button>
      </form>

      {login.isError && (
        <p role="alert">
          {invalidCredentials
            ? "E-mail ou senha inválidos."
            : "Não foi possível entrar. Tente novamente."}
        </p>
      )}
    </main>
  );
}
