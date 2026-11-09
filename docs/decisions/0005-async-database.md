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
- Os testes usam SQLite em memória com `aiosqlite`, `httpx2.AsyncClient` e o plugin pytest do
  `anyio`.
- A migração foi feita no P0, antes de existirem módulos reais.

## Consequências

- Dependências novas: `sqlalchemy[asyncio]` (traz o `greenlet`) e `aiosqlite` (dev).
- Acessar atributos com carregamento preguiçoso (lazy loading) fora de `await` gera erro; os
  repositórios devem carregar explicitamente o que o service vai usar.
- SQLite nos testes pode divergir do Postgres em tipos específicos; reavaliar no P1.
