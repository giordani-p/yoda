# Estado atual

Fase concluída: **P0 — Foundation** ([phases/p0.md](phases/p0.md)). Em andamento: **P1 —
Conversational Experience** ([phases/p1.md](phases/p1.md)): autenticação, conversas e assistente
com streaming entregues; falta o fechamento da fase (teste ponta a ponta com a OpenAI). Atualize este documento a cada
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
- Módulo `conversations`: tabelas `conversations` (com exclusão lógica por `deleted_at`) e
  `messages` (papel, conteúdo, modelo e tokens). Rotas para criar, listar, consultar e excluir
  conversas e para listar mensagens (`/api/v1/conversations`), todas restritas ao usuário
  autenticado; conversa excluída ou de outro usuário responde 404. Paginação por cursor opaco
  (`limit` + `nextCursor`): conversas da mais recente para a mais antiga; mensagens com a página
  mais recente primeiro, em ordem cronológica. A interface pública grava as mensagens do
  usuário e do assistente (a primeira mensagem define o título, com até 60 caracteres) e lê as
  mensagens recentes.
- Módulo `context`: `ContextProvider` com instruções do sistema versionadas
  (`instructions/v1.md`, pt-BR) e as últimas 20 mensagens (`CONTEXT_RECENT_MESSAGES`).
- Módulo `assistant`: `POST /api/v1/conversations/{conversationId}/messages/stream` com SSE
  ([ADR 0007](decisions/0007-streaming-protocol.md)) e LLM Gateway com a Responses API da
  OpenAI, `store=false`, modelo `gpt-6-luna` em desenvolvimento
  ([ADR 0008](decisions/0008-llm-gateway.md)). A resposta só é gravada quando concluída, com
  modelo e tokens; falha ou desconexão descarta o parcial. Tempos e tokens em log, sem conteúdo.
- O módulo `example` do template foi removido, com sua migration; o histórico de migrations
  começa em `create users table`.
- `/health` fora do contrato: `SELECT 1` no banco, responde `200 {"status": "ok"}` ou
  `503 {"status": "unavailable"}`.
- Testes assíncronos num banco Postgres de teste (`TEST_DATABASE_URL`, criado automaticamente);
  cada teste roda numa transação desfeita ao final. Cobrem as rotas de `users`, `conversations` e `assistant` (com provedor de LLM falso), o
  `OpenAIProvider` (com cliente simulado),
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
- Feature `conversations`: lista lateral (criar, abrir, excluir com confirmação, carregar mais)
  e tela da conversa com o histórico e "Carregar mensagens anteriores". Rotas `/` e
  `/c/:conversationId`, atrás do login. Testes de componente da lista e da tela.
- Feature `assistant`: tela do chat com histórico, resposta ao vivo por streaming, Markdown
  nas respostas (`react-markdown` + `remark-gfm`, sem HTML bruto), botão "Parar" e avisos de
  falha ou interrupção (o parcial fica visível até recarregar, sem ser salvo). Testes do leitor
  de stream, do campo de mensagem, do Markdown e do fluxo do chat.
- Sessão expirada em qualquer chamada (401 `UNAUTHENTICATED`) leva de volta ao login.
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

Orçamento de tokens e resumo da conversa (P2), observabilidade, cache, filas e pipeline de deploy.
