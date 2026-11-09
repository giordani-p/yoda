import createClient from "openapi-fetch";

import { env } from "@/app/config/env";

import type { components, paths } from "./generated/schema";

// Client tipado a partir do contrato. Após mudar o contrato, rode `pnpm generate`.
// `credentials: "include"` envia o cookie de sessão (HttpOnly) para o backend em outra porta.
export const api = createClient<paths>({
  baseUrl: env.apiUrl,
  credentials: "include",
});

export type Schemas = components["schemas"];
