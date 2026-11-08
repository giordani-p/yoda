import createClient from "openapi-fetch";

import { env } from "@/app/config/env";

import type { components, paths } from "./generated/schema";

// Client tipado a partir do contrato. Após mudar o contrato, rode `pnpm generate`.
export const api = createClient<paths>({ baseUrl: env.apiUrl });

export type Schemas = components["schemas"];
