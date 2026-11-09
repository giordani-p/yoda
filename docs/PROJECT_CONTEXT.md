# Contexto do projeto

## Produto e domínio

### Visão

O Yoda é um assistente pessoal de IA independente, acessado inicialmente por uma aplicação web e
usando a API da OpenAI como mecanismo de inteligência. A arquitetura é própria e deve permitir
evoluir gradualmente para memória de longo prazo, pesquisa na web, voz e integrações externas.

O primeiro objetivo não é um agente autônomo, e sim uma experiência conversacional confiável,
contextualizada e extensível, com um núcleo independente de canais.

### Objetivos do primeiro ciclo (MVP)

- Experiência conversacional natural.
- Histórico persistente de conversas e mensagens.
- Contexto preservado dentro de cada conversa.
- Respostas exibidas progressivamente (streaming).
- Frontend e backend desacoplados por contrato de API.
- Execução local, com Docker Compose.

Critérios de sucesso do MVP: aplicação executável localmente de forma reproduzível; usuário
autenticado; criação e gestão de conversas; mensagens persistidas corretamente; respostas da
OpenAI exibidas via streaming; histórico recuperável após reiniciar a aplicação; contexto recente
mantido na conversa; frontend consumindo apenas o contrato da API; módulos respeitando seus limites.

### Fora do escopo do MVP

Memória de longo prazo, busca vetorial (pgvector), pesquisa na web, upload de documentos,
multiagentes, execução de código ou shell, ações autônomas em serviços externos, integrações
(Google, Microsoft etc.), voz, Alexa, AWS, microserviços, Redis, filas e processamento
distribuído. Esses itens só entram nas fases futuras e quando houver necessidade concreta.

### Domínios

| Módulo | Responsabilidade |
|---|---|
| `users` | Identidade, autenticação e dados básicos do usuário |
| `conversations` | Conversas, mensagens, histórico e paginação |
| `assistant` | Orquestração conversacional e integração com o LLM |
| `context` | Montagem e gestão do contexto enviado ao modelo |

Regras de domínio:

- Mesmo com um único usuário, toda consulta e operação respeita o usuário autenticado; um
  usuário nunca acessa conversas de outro.
- **Histórico não é memória.** O histórico registra as mensagens de uma conversa, é recuperado em
  ordem cronológica e faz parte do MVP; é a fonte da verdade das mensagens. A memória de longo
  prazo (informações sobre o usuário, compartilhadas entre conversas, recuperadas por relevância)
  é fase futura e não muda a responsabilidade de `conversations`.
- Há um único agente conversacional, sem handoffs.

### Fluxo de uma interação

1. `assistant` recebe a solicitação validada.
2. Pede o contexto a `context`, que monta as instruções do sistema e as mensagens recentes
   (lidas de `conversations`), respeitando um orçamento de tokens.
3. Solicita a geração ao LLM Gateway e repassa os eventos de streaming ao cliente.
4. Persiste a resposta consolidada em `conversations`.
5. Trata falhas, cancelamentos e desconexões sem deixar mensagens em estado inconsistente.

### Contexto enviado ao modelo

- Composto por instruções do sistema, mensagens recentes e, quando existir, um resumo da conversa.
- Não enviar todo o histórico indiscriminadamente; o contexto deve poder ser reconstruído a partir
  das mensagens persistidas (o resumo complementa, não substitui).
- `context` expõe uma abstração (`ContextProvider`) para que `assistant` não conheça como o
  contexto é obtido. Ela é o ponto de extensão para memória futura.
- As instruções do sistema (identidade, tom, comportamento diante de dúvidas, limites, regras de
  segurança) são centralizadas e versionadas, sem duplicação no código.

### Streaming

- Server-Sent Events (SSE), com tipos de evento padronizados que diferenciam conteúdo, conclusão
  e erro.
- Persistir apenas a mensagem final consolidada, não cada fragmento.
- Os eventos SSE fazem parte do contrato OpenAPI: o `data` de cada evento é um
  `MessageStreamEvent` (união discriminada pelo campo `type`), publicado pelo SSE nativo do
  FastAPI e gerado como tipo no frontend. A ordem dos eventos e o comportamento em falha ficam na
  descrição da operação.

### LLM Gateway

O acesso à OpenAI fica isolado em uma integração (`LLMProvider`, em `assistant`), que encapsula o
SDK oficial, centraliza a escolha do modelo, timeouts, erros, streaming, metadados operacionais e
uso de tokens. Nenhum outro ponto do código chama a OpenAI. A interface reflete os casos de uso
reais, sem abstração genérica excessiva.

### Segurança e privacidade

- Segredos em variáveis de ambiente; `.env` fora do versionamento.
- Autenticação no backend por JWT em cookie HttpOnly, verificado em `app/shared/security/`
  ([ADR 0006](decisions/0006-authentication.md)); usuários criados só pelo terminal.
- Isolamento de dados por usuário: rotas protegidas recebem o `user_id` por `CurrentUserId`.
- Validação de entrada e limite de tamanho das mensagens.
- Erros sem informações internas; logs sem conteúdo sensível desnecessário.
- Mensagens e contexto são enviados à OpenAI: a aplicação não deve afirmar que todo o
  processamento é local. Enviar só o contexto necessário.

### Qualidade

Indicadores acompanhados desde o MVP: tempo até o primeiro fragmento, tempo total de geração,
taxa de sucesso, erros do provedor, tokens e custo estimado por interação, continuidade em
conversas longas.

### Roadmap

| Fase | Objetivo |
|---|---|
| P0 — Foundation | Estrutura e comunicação entre frontend, backend e banco ([phases/p0.md](phases/p0.md)) |
| P1 — Conversational Experience | Autenticação, conversas, mensagens, LLM Gateway, streaming SSE e interface de chat |
| P2 — Context Management | `ContextProvider`, instruções centralizadas, orçamento de tokens, resumo se necessário |
| P3 — Memory e Research | Memória (perfil, episódica, conhecimento), pgvector, pesquisa na web |
| P4 — Personalization e Evaluation | Preferências, evals, métricas de latência e custo, observabilidade |
| P5 — Expansion | Ferramentas, integrações, aprovação humana, voz, outros canais, avaliação de AWS |

Implementar uma fase por vez, sem antecipar funcionalidades das seguintes. A especificação de cada
fase fica em `docs/phases/pN.md` e é criada ao iniciar a fase.

## Arquitetura

### API First

- `contracts/openapi/openapi.yaml` é a fonte da verdade da API e muda **antes** do código.
- O backend é verificado contra o contrato por `tests/test_contract.py`, que compara rotas,
  métodos, status codes, `operationId` e, nos schemas, propriedades e campos obrigatórios.
  Tipos e validações não são comparados.
- O frontend consome tipos gerados do contrato (`pnpm generate`), versionados em
  `apps/frontend/src/services/api/generated/`.
- Endpoints versionados sob `/api/v1`; schemas de entrada e saída explícitos, sem expor entidades
  internas do domínio.

### Monolito modular

O backend é um único deploy dividido em módulos em `app/modules/`.

| Pasta | Responsabilidade | Pode importar |
|---|---|---|
| `app/core/` | Configuração, logging, erros e envelope de erro | Bibliotecas externas |
| `app/shared/` | Infraestrutura técnica comum (banco, schema base, identificação do usuário na requisição). Nunca regra de negócio | `core` |
| `app/modules/<nome>/` | Um contexto de negócio | `core`, `shared`, a interface pública dos módulos permitidos |
| `app/api/` | Só agrega os routers dos módulos | `modules` |

Dependências permitidas entre módulos (ADR 0004), sempre pela interface pública
(`app/modules/<nome>/__init__.py`):

```
assistant ──> context ──> conversations
    └───────────────────────> conversations
users      (independente; os módulos recebem o user_id por app/shared/security/)
```

Regras verificadas pelo `import-linter`:

- nenhum módulo importa outro, exceto as arestas acima, e só o pacote raiz do módulo de destino;
- dentro de cada módulo, um arquivo só importa os que estão abaixo dele
  (`router` → `service` → `repository` → `models`);
- `core` e `shared` não importam `modules` nem `api`.

### Estrutura de um módulo

```
modules/<nome>/
  __init__.py     interface pública (o que outros módulos e app/api podem usar)
  router.py       rotas HTTP; o `name` de cada rota é o operationId do contrato
  schemas.py      schemas da API, espelham o contrato (JSON em camelCase)
  service.py      regras de negócio e casos de uso
  repository.py   acesso a dados
  models.py       models SQLAlchemy
```

Estrutura plana, com a ordem `router` → `service` → `repository` → `models` verificada pelo
`import-linter` (ADR 0002). Interfaces explícitas (`Protocol`) só onde há integração externa ou
ponto de extensão: `LLMProvider` em `assistant` e `ContextProvider` em `context`. Não aplicar DDD
tático sem um problema real que o justifique. `modules/conversations/` serve de referência.


### Banco de dados

- PostgreSQL com SQLAlchemy 2 **assíncrono** (`AsyncSession`, driver psycopg 3) na aplicação
  (ADR 0005). O Alembic roda em modo síncrono com a mesma `DATABASE_URL`.
- Uma única árvore de migrations; o Alembic carrega o `models.py` de todos os módulos.
- Os testes usam um banco Postgres de teste (`TEST_DATABASE_URL`), criado automaticamente; cada
  teste roda numa transação desfeita ao final.

### Health check

`GET /health` (fora do contrato) executa `SELECT 1`: responde `200 {"status": "ok"}` ou
`503 {"status": "unavailable"}` se o banco não responder. É usado pelo healthcheck do Docker.

### Frontend

- `src/features/<nome>/` espelha o módulo do backend e contém a página, os hooks de dados
  (`api.ts`, com TanStack Query) e os testes da funcionalidade.
- `src/components/`, `src/hooks/` e `src/lib/` ficam só para o que é genérico e reutilizado
  por mais de uma feature.

### Erros da API

Toda resposta de erro segue `{ "error": { "code", "message", "details" } }`. Erros de negócio
são subclasses de `AppError` em `app/core/exceptions.py`.

## Decisões

As decisões de arquitetura ficam em [decisions/](decisions/). A especificação original do projeto
está arquivada em [archive/spec.md](archive/spec.md) como registro histórico; este documento, as
fases e os ADRs prevalecem sobre ela.
