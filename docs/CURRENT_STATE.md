# Estado atual

Fase concluída: **P0 — Foundation** ([phases/p0.md](phases/p0.md)). Em andamento: **P1 —
Conversational Experience** ([phases/p1.md](phases/p1.md)): autenticação entregue; conversas e
assistente ainda não. Atualize este documento a cada
entrega que mude o que está implementado.

## Backend

- FastAPI com configuração por variáveis de ambiente, logging, CORS e envelope de erro padrão.
- Postgres via SQLAlchemy 2 **assíncrono** (`AsyncSession`, psycopg 3) e Alembic (síncrono), com
  uma migration inicial.
- Módulo `users`: tabela `users` (id UUID, e-mail único, nome, hash argon2), login
  (`POST /api/v1/auth/login`), logout (`POST /api/v1/auth/logout`) e usuário autenticado
  (`GET /api/v1/users/me`). Usuários são criados só pelo terminal (`make create-user`).
- Sessão por JWT num cookie HttpOnly `yoda_session` (7 dias, sem refresh), emitido e verificado
  por `app/shared/security/` sem acesso ao banco ([ADR 0006](decisions/0006-authentication.md)).
  CORS com credenciais.
- Módulos `conversations`, `assistant` e `context` criados apenas com o `__init__.py`, sem rotas,
  models ou regras.
- Módulo `example` com listagem, criação e consulta por id (`/api/v1/examples`);
  permanece até o primeiro endpoint real do P1.
- `/health` fora do contrato: `SELECT 1` no banco, responde `200 {"status": "ok"}` ou
  `503 {"status": "unavailable"}`.
- Testes assíncronos num banco Postgres de teste (`TEST_DATABASE_URL`, criado automaticamente);
  cada teste roda numa transação desfeita ao final. Cobrem as rotas do `example` e de `users`,
  o cadastro de usuários, a configuração, o health check e o contrato (este sem banco).
- `import-linter` verifica: grafo de dependências entre módulos (`assistant → context`,
  `assistant → conversations`, `context → conversations`, só pela interface pública), ordem
  `router` → `service` → `repository` → `models` dentro de cada módulo e isolamento de
  `core`/`shared`.

## Frontend

- React + Vite + TypeScript, com React Router e TanStack Query.
- Client tipado gerado a partir do contrato (`openapi-typescript` + `openapi-fetch`).
- Feature `auth`: tela de login (`/login`), guarda das rotas autenticadas e menu com nome do
  usuário e botão "Sair". Testes de componente do login e da guarda.
- Feature `example` com listagem e cadastro, atrás do login, com um teste de componente.
- Nome exibido: Yoda.

## Infraestrutura e qualidade

- `docker-compose.yml` com Postgres, backend (aplica as migrations ao subir) e frontend (nginx).
  Backend e banco têm healthcheck; o do backend depende do banco via `/health`.
- O Alembic carrega automaticamente o `models.py` de todos os módulos.
- `Makefile` com comandos de setup, desenvolvimento, testes, lint e contrato; `make test` sobe o
  Postgres antes de rodar os testes.
- Pre-commit com ruff, import-linter, ESLint e Prettier.
- CI no GitHub Actions: lint, testes (com serviço Postgres), teste de contrato, checagem do
  client gerado e build.

## Não implementado

Conversas e mensagens, integração com a OpenAI (LLM Gateway), streaming SSE,
interface de chat, observabilidade, cache, filas e pipeline de deploy.
