# Contexto do projeto

## Produto e domínio

> Preencha ao iniciar um projeto a partir do template: o problema resolvido, os usuários,
> os principais conceitos do domínio e as regras de negócio relevantes.

## Arquitetura

### API First

- `contracts/openapi/openapi.yaml` é a fonte da verdade da API e muda **antes** do código.
- O backend é verificado contra o contrato por `tests/test_contract.py`, que compara rotas,
  métodos, status codes, `operationId` e, nos schemas, propriedades e campos obrigatórios.
  Tipos e validações não são comparados.
- O frontend consome tipos gerados do contrato (`pnpm generate`), versionados em
  `apps/frontend/src/services/api/generated/`.

### Monolito modular

O backend é um único deploy dividido em módulos independentes em `app/modules/`.

| Pasta | Responsabilidade | Pode importar |
|---|---|---|
| `app/core/` | Configuração, logging, erros e envelope de erro | Bibliotecas externas |
| `app/shared/` | Infraestrutura técnica comum (banco, schema base). Nunca regra de negócio | `core` |
| `app/modules/<nome>/` | Um contexto de negócio | `core`, `shared`, a interface pública de outro módulo |
| `app/api/` | Só agrega os routers dos módulos | `modules` |

Regras verificadas pelo `import-linter`:

- um módulo não importa outro módulo;
- `core` e `shared` não importam `modules` nem `api`.

Hoje os módulos são totalmente independentes. Se dois módulos precisarem se comunicar, decida
o mecanismo (interface pública, eventos) e registre um ADR antes de afrouxar a regra.

### Estrutura de um módulo

```
modules/<nome>/
  __init__.py     interface pública (o que outros podem usar)
  router.py       rotas HTTP; o `name` de cada rota é o operationId do contrato
  schemas.py      schemas da API, espelham o contrato (JSON em camelCase)
  service.py      regras de negócio
  repository.py   acesso a dados
  models.py       models SQLAlchemy
```

Para evoluir um módulo para DDD, reorganize os arquivos dentro dele em `domain/`,
`application/` e `infrastructure/`, sem afetar os outros módulos.

### Frontend

- `src/features/<nome>/` espelha o módulo do backend e contém a página, os hooks de dados
  (`api.ts`, com TanStack Query) e os testes da funcionalidade.
- `src/components/`, `src/hooks/` e `src/lib/` ficam só para o que é genérico e reutilizado
  por mais de uma feature.

### Erros da API

Toda resposta de erro segue `{ "error": { "code", "message", "details" } }`. Erros de negócio
são subclasses de `AppError` em `app/core/exceptions.py`.

## Decisões

As decisões de arquitetura ficam em [decisions/](decisions/).
