# Estado atual

Fase concluída: **P0 — Foundation** ([phases/p0.md](phases/p0.md)). Atualize este documento a cada
entrega que mude o que está implementado.

## Backend

- FastAPI com configuração por variáveis de ambiente, logging, CORS e envelope de erro padrão.
- Postgres via SQLAlchemy 2 **assíncrono** (`AsyncSession`, psycopg 3) e Alembic (síncrono), com
  uma migration inicial.
- Módulos `users`, `conversations`, `assistant` e `context` criados apenas com o `__init__.py`
  (docstring de responsabilidade), sem rotas, models ou regras.
- `app/shared/security/` criado vazio, reservado para a identificação do usuário autenticado.
- Módulo `example` com listagem, criação e consulta por id (`/api/v1/examples`);
  permanece até o primeiro endpoint real do P1.
- `/health` fora do contrato: `SELECT 1` no banco, responde `200 {"status": "ok"}` ou
  `503 {"status": "unavailable"}`.
- Testes assíncronos (SQLite em memória com aiosqlite): rotas do `example`, health check e teste
  de contrato.
- `import-linter` verifica: grafo de dependências entre módulos (`assistant → context`,
  `assistant → conversations`, `context → conversations`, só pela interface pública), ordem
  `router` → `service` → `repository` → `models` dentro de cada módulo e isolamento de
  `core`/`shared`.

## Frontend

- React + Vite + TypeScript, com React Router e TanStack Query.
- Client tipado gerado a partir do contrato (`openapi-typescript` + `openapi-fetch`).
- Feature `example` com listagem e cadastro, com um teste de componente.
- Nome exibido: Yoda.

## Infraestrutura e qualidade

- `docker-compose.yml` com Postgres, backend (aplica as migrations ao subir) e frontend (nginx).
  Backend e banco têm healthcheck; o do backend depende do banco via `/health`.
- O Alembic carrega automaticamente o `models.py` de todos os módulos.
- `Makefile` com comandos de setup, desenvolvimento, testes, lint e contrato.
- Pre-commit com ruff, import-linter, ESLint e Prettier.
- CI no GitHub Actions: lint, testes, teste de contrato, checagem do client gerado e build.

## Não implementado

Autenticação, conversas e mensagens, integração com a OpenAI (LLM Gateway), streaming SSE,
interface de chat, observabilidade, cache, filas e pipeline de deploy.
