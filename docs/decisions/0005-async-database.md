# 0005 — Acesso assíncrono ao banco

**Status:** aceita

## Contexto

O template usava SQLAlchemy síncrono. O Yoda depende de operações assíncronas: streaming SSE das
respostas, chamadas ao SDK da OpenAI e interfaces `async` (`ContextProvider`, `LLMProvider`).
Misturar código síncrono de banco com rotas assíncronas exigiria executar repositórios em
threadpool e manter dois modelos de execução.

## Decisão

- A aplicação usa SQLAlchemy 2 assíncrono (`create_async_engine`, `AsyncSession`), com o driver
  psycopg 3, que já atende os dois modos (sem trocar a `DATABASE_URL`).
- Rotas, casos de uso e repositórios são `async`.
- O Alembic continua síncrono, com a mesma URL.
- Os testes usam `httpx2.AsyncClient` e o plugin pytest do `anyio`. ~~SQLite em memória com
  `aiosqlite`.~~ Revisto no P1: Postgres (ver abaixo).
- A migração foi feita no P0, antes de existirem módulos reais.

## Consequências

- Dependência nova: `sqlalchemy[asyncio]` (traz o `greenlet`).
- Acessar atributos com carregamento preguiçoso (lazy loading) fora de `await` gera erro; os
  repositórios devem carregar explicitamente o que o service vai usar.
- ~~SQLite nos testes pode divergir do Postgres em tipos específicos; reavaliar no P1.~~

## Revisão (09/11/2026) — testes em Postgres

O P1 introduz UUID, `timestamptz`, chaves estrangeiras e índices compostos, em que o SQLite se
comporta diferente do Postgres. Os testes passam a usar um banco Postgres de teste
(`TEST_DATABASE_URL`), criado automaticamente se não existir. O schema é recriado uma vez por
execução e cada teste roda numa transação desfeita ao final. `make test` sobe o Postgres do
Docker Compose; no CI, o workflow usa um serviço Postgres. O `aiosqlite` foi removido.
Consequência: rodar os testes exige um Postgres disponível.
