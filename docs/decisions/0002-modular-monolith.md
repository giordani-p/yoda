# 0002 — Monolito modular

**Status:** aceita

## Contexto

Projetos novos precisam de entrega rápida, mas devem poder evoluir para DDD ou separar
partes no futuro sem reescrita.

## Decisão

- Um único deploy, com o backend dividido em módulos em `app/modules/`.
- Cada módulo é dono das próprias rotas, schemas, regras, acesso a dados e models.
- `app/api/` só agrega os routers.
- O `import-linter` impede imports entre módulos (exceto os definidos no ADR 0004) e de
  `core`/`shared` para `modules`.
- Estrutura interna simples (router, schemas, service, repository, models). Camadas DDD
  entram por módulo, apenas quando necessário.

## Consequências

- Um módulo pode ser reorganizado ou extraído sem afetar os outros.
- ~~Comunicação entre módulos ainda não está definida; quando for necessária, registrar um ADR.~~
  Definida no ADR 0004.
- As migrations ficam em uma única árvore do Alembic, compartilhada por todos os módulos.

## Revisão (09/11/2026) — camadas por arquivo

A especificação do Yoda sugeria as pastas `domain/`, `application/`, `infrastructure/` e
`presentation/` em cada módulo. Elas chegaram a ser adotadas no P0 e foram revertidas antes de
qualquer módulo real: o custo (entidades duplicando os models, portas para cada repositório,
mapeamento ORM → entidade, pastas vazias) não se paga em módulos majoritariamente de CRUD e
orquestração. A própria especificação desaconselha DDD indiscriminado e permite ajustar a
estrutura.

Decisão:

- Os módulos mantêm a estrutura plana. Os models do SQLAlchemy são usados diretamente pelo
  service.
- A separação de responsabilidades é verificada por arquivo: um contrato `layers` do
  `import-linter` garante a ordem `router` → `service` → `repository` → `models` (cada camada é
  opcional). `schemas.py` fica fora da ordem e pode ser usado pelo router e pelo service.
- Interfaces explícitas (`Protocol`) só onde há integração externa ou ponto de extensão real:
  o `LLMProvider` em `assistant` e o `ContextProvider` em `context`, criados quando esses
  módulos forem implementados.
- Um módulo que ficar complexo pode ser reorganizado em camadas internamente, sem afetar os outros.
