# Yoda

Assistente pessoal de IA com **Python/FastAPI** no backend, **React/TypeScript** no frontend e a API da OpenAI como mecanismo de inteligência, seguindo **API First** e **monolito modular** organizado por domínios funcionais.

O contexto do produto e as regras de arquitetura estão em [docs/PROJECT_CONTEXT.md](docs/PROJECT_CONTEXT.md); o que já está implementado, em [docs/CURRENT_STATE.md](docs/CURRENT_STATE.md).

## Pré-requisitos

- [uv](https://docs.astral.sh/uv/) (Python 3.12+)
- Node 24 (`nvm install` usa o `.nvmrc`) e [pnpm](https://pnpm.io/)
- Docker

## Primeiros passos

```bash
make setup     # cria o .env a partir do .env.example
make install   # instala as dependências do backend e do frontend
make up        # sobe banco, backend e frontend no Docker
```

- Frontend: http://localhost:5173
- Backend: http://localhost:8000 (documentação interativa em `/docs`)

## Desenvolvimento local (com reload)

```bash
make db             # sobe só o Postgres
make migrate        # aplica as migrations
make dev-backend    # em um terminal
make dev-frontend   # em outro terminal
```

Rode `make help` para ver todos os comandos.

## Estrutura

```
apps/
  backend/            FastAPI (uv, SQLAlchemy, Alembic, ruff, pytest, import-linter)
    app/
      core/           configuração, logging e erros
      shared/         infraestrutura técnica comum (banco, schema base, segurança)
      api/            só agrega os routers dos módulos
      modules/        users, conversations, assistant, context (e example, até o P1)
        <nome>/       router, schemas, service, repository, models
    migrations/       Alembic
    tests/            espelha app/, inclui o teste de contrato
  frontend/           React + Vite (TanStack Query, React Router, Vitest)
    src/
      app/            providers e configuração
      features/       um diretório por funcionalidade, espelhando os módulos
      services/api/   client tipado gerado a partir do contrato
contracts/openapi/    contrato da API (fonte da verdade)
docs/                 contexto, estado atual, fases, decisões (ADRs) e spec arquivada
```

As regras de arquitetura estão em [docs/PROJECT_CONTEXT.md](docs/PROJECT_CONTEXT.md).

## Fluxo API First

1. Altere o contrato em `contracts/openapi/openapi.yaml`.
2. Rode `make generate-client` para atualizar os tipos do frontend.
3. Implemente no backend até o teste de contrato passar (`make contract-check`).
4. Use os tipos gerados no frontend.

O CI falha se o backend divergir do contrato ou se o client gerado estiver desatualizado.

## Criando um novo módulo

Os módulos do produto já existem como esqueletos. Para criar um novo (ou preencher um existente):

1. Descreva os endpoints e schemas no contrato.
2. Siga `apps/backend/app/modules/example/` como referência (`router.py`, `schemas.py`, `service.py`, `repository.py`, `models.py`).
3. Exporte no `__init__.py` do módulo a interface pública (por exemplo, o `router`) e registre o router em `app/api/router.py`.
4. Rode `make migration name=create_<nome>` (o `models.py` de todos os módulos é carregado automaticamente).
5. Crie os testes em `tests/modules/<nome>/`.
6. No frontend, crie `src/features/<nome>/` seguindo `features/example/`.

Um módulo só pode usar outro através do que ele exporta no próprio `__init__.py`, e apenas nas dependências permitidas pelo [ADR 0004](docs/decisions/0004-module-communication.md). Dentro de cada módulo, um arquivo só importa os que estão abaixo dele (`router` → `service` → `repository` → `models`). O `import-linter` verifica as duas regras.

## Qualidade

```bash
make lint      # ruff, import-linter, eslint, prettier, tsc
make test      # pytest (sobe o Postgres do Docker) e vitest
make format
pre-commit install   # opcional: roda os linters a cada commit
```
