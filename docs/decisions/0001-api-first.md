# 0001 — API First com contrato OpenAPI

**Status:** aceita

## Contexto

O FastAPI gera o OpenAPI a partir do código (code-first). Sem uma referência externa, o
contrato muda junto com a implementação e o frontend descobre as mudanças tarde.

## Decisão

- O contrato fica em `contracts/openapi/openapi.yaml` e é alterado antes do código.
- O backend é escrito à mão e verificado contra o contrato por um teste pytest de comparação
  estrutural, sem gerar código a partir do spec.
- O frontend usa tipos gerados do contrato com `openapi-typescript` e chamadas com `openapi-fetch`.

## Consequências

- Divergências entre backend e contrato quebram o CI.
- O teste não compara tipos nem validações; essas diferenças passam despercebidas. Se isso
  virar um problema, avaliar uma ferramenta como `oasdiff`.
- O `operationId` é definido pelo `name` de cada rota no FastAPI.

## Revisão (08/11/2026)

A especificação inicial do Yoda citava "OpenAPI gerado pelo FastAPI" e, ao mesmo tempo, exigia
contratos desenhados antes da implementação. A decisão contract-first foi mantida, porque é ela que
garante o contrato antes do código; o OpenAPI gerado pelo FastAPI é usado apenas para verificar a
implementação contra o contrato. O protocolo de streaming (SSE) não é representado no OpenAPI e
será documentado separadamente no P1.
