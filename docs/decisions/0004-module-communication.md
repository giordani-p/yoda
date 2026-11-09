# 0004 — Comunicação entre módulos

**Status:** aceita

## Contexto

O ADR 0002 deixava a comunicação entre módulos indefinida e o `import-linter` proibia qualquer
import entre eles. O fluxo do Yoda exige dependências: `assistant` orquestra a interação usando
`context` e `conversations`, e `context` monta o contexto a partir do histórico de
`conversations`. Todos precisam saber quem é o usuário autenticado.

## Decisão

- Módulos se comunicam por chamada direta à **interface pública** do outro módulo: somente o que
  é exportado em `app/modules/<nome>/__init__.py`. Subpacotes internos de outro módulo nunca são
  importados.
- Dependências permitidas (grafo direcionado, sem ciclos):
  - `assistant` → `context`
  - `assistant` → `conversations`
  - `context` → `conversations`
- `users` é independente: nenhum módulo o importa. O identificador do usuário autenticado chega
  aos módulos por `app/shared/security/` (a ser implementado no P1); regras de negócio de
  usuários continuam em `users`.
- Eventos internos ou mensageria não são usados.
- O contrato `independence` do `import-linter` mantém tudo proibido por padrão e libera apenas
  as arestas acima, e só para o pacote raiz do módulo de destino.

## Consequências

- Uma nova dependência entre módulos exige atualizar este ADR e o `ignore_imports` do contrato
  em `apps/backend/pyproject.toml`.
- A interface pública de cada módulo precisa ser desenhada explicitamente (o que exportar no
  `__init__.py`).
- Um import interno de outro módulo, ou uma aresta não prevista, quebra o lint e o CI.
