# 0002 — Monolito modular

**Status:** aceita

## Contexto

Projetos novos precisam de entrega rápida, mas devem poder evoluir para DDD ou separar
partes no futuro sem reescrita.

## Decisão

- Um único deploy, com o backend dividido em módulos em `app/modules/`.
- Cada módulo é dono das próprias rotas, schemas, regras, acesso a dados e models.
- `app/api/` só agrega os routers.
- O `import-linter` impede imports entre módulos e de `core`/`shared` para `modules`.
- Estrutura interna simples (router, schemas, service, repository, models). Camadas DDD
  entram por módulo, apenas quando necessário.

## Consequências

- Um módulo pode ser reorganizado ou extraído sem afetar os outros.
- Comunicação entre módulos ainda não está definida; quando for necessária, registrar um ADR.
- As migrations ficam em uma única árvore do Alembic, compartilhada por todos os módulos.
