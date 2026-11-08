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
