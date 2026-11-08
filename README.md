# my-project

Template base para novos projetos com **Python/FastAPI** no backend e **React/TypeScript** no frontend, seguindo **API First** e **monolito modular**.

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
      shared/         infraestrutura técnica comum (banco, schema base)
      api/            só agrega os routers dos módulos
      modules/        um pacote por módulo de negócio
    migrations/       Alembic
    tests/            espelha app/, inclui o teste de contrato
  frontend/           React + Vite (TanStack Query, React Router, Vitest)
    src/
      app/            providers e configuração
      features/       um diretório por funcionalidade, espelhando os módulos
      services/api/   client tipado gerado a partir do contrato
contracts/openapi/    contrato da API (fonte da verdade)
docs/                 contexto, estado atual, fases e decisões (ADRs)
```

As regras de arquitetura estão em [docs/PROJECT_CONTEXT.md](docs/PROJECT_CONTEXT.md).

## Fluxo API First

1. Altere o contrato em `contracts/openapi/openapi.yaml`.
2. Rode `make generate-client` para atualizar os tipos do frontend.
3. Implemente no backend até o teste de contrato passar (`make contract-check`).
4. Use os tipos gerados no frontend.

O CI falha se o backend divergir do contrato ou se o client gerado estiver desatualizado.

## Criando um novo módulo

1. Descreva os endpoints e schemas no contrato.
2. Copie `apps/backend/app/modules/example/` para `app/modules/<nome>/` e ajuste.
3. Registre o router em `app/api/router.py`.
4. Rode `make migration name=create_<nome>` (os models de todos os módulos são carregados automaticamente).
5. Crie os testes em `tests/modules/<nome>/`.
6. No frontend, crie `src/features/<nome>/` seguindo `features/example/`.

Um módulo só pode ser usado por outro através do que ele exporta no próprio `__init__.py`. O `import-linter` bloqueia imports diretos entre módulos.

## Qualidade

```bash
make lint      # ruff, import-linter, eslint, prettier, tsc
make test      # pytest e vitest
make format
pre-commit install   # opcional: roda os linters a cada commit
```

## Ao usar este template

- Troque `my-project` pelo nome do projeto (`.env.example`, `contracts/openapi/openapi.yaml`, `apps/backend/app/core/config.py`, `index.html`, `AppLayout.tsx`, este README).
- Remova o módulo `example` (backend, contrato, migration e feature do frontend) quando o primeiro módulo real existir.
