// Origem do backend. As rotas do contrato já incluem o prefixo /api/v1.
export const env = {
  apiUrl: import.meta.env.VITE_API_URL ?? "http://localhost:8000",
};
