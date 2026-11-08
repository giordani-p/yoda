# Estado atual

Estado do template base. Atualize este documento a cada entrega que mude o que está implementado.

## Backend

- FastAPI com configuração por variáveis de ambiente, logging, CORS e envelope de erro padrão.
- Banco Postgres via SQLAlchemy 2 (síncrono) e Alembic, com uma migration inicial.
- Módulo `example` com listagem, criação e consulta por id (`/api/v1/examples`).
- `/health` fora do contrato.
- Testes: rotas do módulo `example` (SQLite em memória) e teste de contrato.
- Fronteiras entre módulos verificadas pelo `import-linter`.

## Frontend

- React + Vite + TypeScript, com React Router e TanStack Query.
- Client tipado gerado a partir do contrato (`openapi-typescript` + `openapi-fetch`).
- Feature `example` com listagem e cadastro, com um teste de componente.

## Infraestrutura e qualidade

- `docker-compose.yml` com Postgres, backend (aplica as migrations ao subir) e frontend (nginx).
  Backend e banco têm healthcheck; cada serviço só sobe quando sua dependência está saudável.
- O Alembic carrega automaticamente o `models.py` de todos os módulos.
- `Makefile` com comandos de setup, desenvolvimento, testes, lint e contrato.
- Pre-commit com ruff, import-linter, ESLint e Prettier.
- CI no GitHub Actions: lint, testes, teste de contrato, checagem do client gerado e build.

## Não implementado

Autenticação, observabilidade, cache, filas e pipeline de deploy.
