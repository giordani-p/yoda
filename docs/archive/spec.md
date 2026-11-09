# Personal AI Assistant --- Plano de Arquitetura e Implementação

**Versão:** 1.0\
**Data:** 08/11/2026\
**Status:** Plano inicial para implementação local

------------------------------------------------------------------------

## 1. Visão do projeto

Construir um assistente pessoal de IA independente, inicialmente
acessível por uma aplicação web, utilizando a API da OpenAI como
mecanismo de inteligência.

O projeto será desenvolvido com arquitetura própria, componentes open
source consolidados e uma estrutura que permita evoluir gradualmente
para memória de longo prazo, pesquisa na web, voz e integrações com
serviços externos.

### Objetivos do primeiro ciclo

-   Oferecer uma experiência conversacional natural.
-   Manter histórico persistente de conversas e mensagens.
-   Preservar o contexto dentro de cada conversa.
-   Exibir respostas progressivamente por streaming.
-   Manter frontend e backend desacoplados por contratos de API.
-   Organizar o backend por domínios funcionais, em um monólito modular.
-   Executar toda a aplicação localmente durante a fase inicial.

### Princípios

-   API First.
-   Modular Monolith.
-   Organização orientada a domínios funcionais.
-   Baixo acoplamento entre módulos.
-   Separação entre domínio, aplicação, infraestrutura e apresentação.
-   Começar simples e evoluir incrementalmente.
-   Privacidade e segurança desde o início.
-   Não implementar memória de longo prazo, pesquisa web ou integrações
    externas no primeiro MVP.

------------------------------------------------------------------------

## 2. Decisões arquiteturais

  Tema                      Decisão
  ------------------------- ------------------------------
  Arquitetura               Monólito modular
  Organização               Domínios funcionais
  Desenvolvimento da API    API First
  Contrato                  OpenAPI
  Frontend                  React + TypeScript
  Backend                   Python + FastAPI
  LLM                       OpenAI API
  Persistência              PostgreSQL
  ORM                       SQLAlchemy 2
  Migrations                Alembic
  Comunicação de resposta   HTTP Streaming / SSE
  Execução inicial          Local, com Docker Compose
  Memória de longo prazo    Fora do escopo inicial
  Pesquisa na web           Fora do escopo inicial
  Infraestrutura AWS        Avaliar em fase posterior
  Multiagentes              Não implementar inicialmente

### 2.1. API First

A API será definida como contrato entre frontend e backend. Os contratos
devem ser desenhados antes da implementação das telas e dos casos de uso
correspondentes.

Diretrizes:

-   Versionar endpoints sob `/api/v1`.
-   Definir schemas explícitos de entrada e saída.
-   Padronizar respostas de erro.
-   Documentar autenticação e autorização.
-   Documentar o protocolo de streaming.
-   Utilizar OpenAPI gerado pelo FastAPI como especificação da API.
-   Evitar expor entidades internas do domínio diretamente nos contratos
    HTTP.
-   Manter o frontend independente da estrutura interna do backend.

O frontend deve consumir a API como qualquer outro cliente. Isso
permitirá adicionar futuramente aplicativos móveis, interfaces de voz ou
outros canais sem acoplar esses canais ao núcleo do assistente.

### 2.2. Modular Monolith

A aplicação backend será implantada inicialmente como uma única unidade,
mas organizada em módulos com responsabilidades e limites bem definidos.

Não criar microserviços nesta etapa.

Cada módulo deve concentrar suas próprias regras, casos de uso,
interfaces e implementações de infraestrutura. Um módulo não deve
acessar diretamente tabelas, repositórios ou detalhes internos de outro
módulo.

A comunicação entre módulos deve ocorrer por interfaces públicas,
serviços de aplicação ou contratos internos explícitos.

### 2.3. Organização por domínios funcionais

Domínios iniciais:

  Módulo            Responsabilidade
  ----------------- ------------------------------------------------------
  `users`           Identidade, autenticação e dados básicos do usuário
  `conversations`   Conversas, mensagens, histórico e sessões
  `assistant`       Orquestração conversacional e integração com o LLM
  `context`         Montagem e gestão do contexto enviado ao modelo
  `shared`          Recursos transversais e infraestrutura compartilhada

Os módulos `assistant` e `context` devem ser independentes de detalhes
específicos do frontend. O módulo `context` será a extensão natural para
incorporar memória de longo prazo futuramente.

------------------------------------------------------------------------

## 3. Arquitetura lógica

``` text
PERSONAL ASSISTANT UI
React + TypeScript
        |
        | HTTP / SSE
        v
BACKEND API
FastAPI
        |
        v
PRESENTATION LAYER
Routes / Controllers / Schemas
        |
        v
APPLICATION LAYER
Use Cases / Application Services
        |
        +-------------------------------+
        |               |               |
        v               v               v
   CONVERSATIONS    ASSISTANT        CONTEXT
        |               |               |
        v               v               v
   Repositories    LLM Gateway     Context Builder
        |               |               |
        |               v               |
        |          OpenAI API            |
        |                               |
        +---------------+---------------+
                        |
                        v
                 PostgreSQL
```

O diagrama representa os principais limites lógicos. A implementação
inicial deve permanecer em um único backend e processo de aplicação, sem
criar serviços distribuídos.

------------------------------------------------------------------------

## 4. Stack tecnológica

  Camada           Tecnologia                Uso
  ---------------- ------------------------- -----------------------------------
  Frontend         React + TypeScript        Interface web
  Backend          Python + FastAPI          API e casos de uso
  LLM              OpenAI API / Python SDK   Geração de respostas
  Banco de dados   PostgreSQL                Usuários, conversas e mensagens
  ORM              SQLAlchemy 2              Persistência
  Migrations       Alembic                   Evolução do schema
  Streaming        SSE / HTTP Streaming      Entrega progressiva das respostas
  Ambiente local   Docker Compose            Execução dos componentes

### Diretrizes técnicas

-   Utilizar o SDK oficial da OpenAI inicialmente.
-   Isolar a integração com o provedor em um `LLM Gateway`.
-   Não espalhar chamadas diretas à OpenAI pelos módulos.
-   Utilizar PostgreSQL como persistência principal.
-   Não adicionar pgvector enquanto não existir necessidade de busca
    vetorial.
-   Não adicionar Redis, filas ou cache sem um caso de uso concreto.
-   Manter configurações e segredos fora do código-fonte.
-   Fixar e documentar versões das dependências.

------------------------------------------------------------------------

## 5. Estrutura sugerida do repositório

A estrutura abaixo é uma referência inicial. Ajustes são permitidos
desde que preservem os limites entre módulos.

``` text
personal-assistant/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   │
│   │   ├── modules/
│   │   │   ├── users/
│   │   │   │   ├── domain/
│   │   │   │   ├── application/
│   │   │   │   ├── infrastructure/
│   │   │   │   └── presentation/
│   │   │   │
│   │   │   ├── conversations/
│   │   │   │   ├── domain/
│   │   │   │   ├── application/
│   │   │   │   ├── infrastructure/
│   │   │   │   └── presentation/
│   │   │   │
│   │   │   ├── assistant/
│   │   │   │   ├── domain/
│   │   │   │   ├── application/
│   │   │   │   ├── infrastructure/
│   │   │   │   └── presentation/
│   │   │   │
│   │   │   └── context/
│   │   │       ├── domain/
│   │   │       ├── application/
│   │   │       ├── infrastructure/
│   │   │       └── presentation/
│   │   │
│   │   └── shared/
│   │       ├── database/
│   │       ├── security/
│   │       └── common/
│   │
│   ├── migrations/
│   ├── tests/
│   ├── pyproject.toml
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

### Responsabilidade das camadas

-   **Domain:** entidades, value objects, regras e interfaces centrais
    do domínio. Não depende de frameworks ou infraestrutura.
-   **Application:** casos de uso, coordenação das operações e portas
    necessárias.
-   **Infrastructure:** implementações concretas de banco, provedores
    externos e integrações.
-   **Presentation:** rotas HTTP, controllers, schemas e adaptação dos
    contratos externos.

Não aplicar DDD tático completo indiscriminadamente. Utilizar entidades,
agregados, eventos de domínio e outros padrões somente quando resolverem
um problema real.

### Regras de dependência

1.  Domain não depende de Application, Infrastructure ou Presentation.
2.  Application depende do Domain e de abstrações.
3.  Infrastructure implementa as abstrações definidas pelas camadas
    internas.
4.  Presentation chama casos de uso da Application.
5.  Um módulo não acessa diretamente a infraestrutura interna de outro
    módulo.
6.  Dependências entre módulos devem ser explícitas e direcionadas às
    interfaces públicas.
7.  `shared` não deve se transformar em um local genérico para regras de
    negócio.

------------------------------------------------------------------------

## 6. Módulos e responsabilidades

### 6.1. Users

Responsável por identidade e autenticação.

Escopo inicial:

-   Cadastro ou provisionamento do usuário.
-   Autenticação.
-   Identificação do usuário nas requisições.
-   Autorização e isolamento dos dados por usuário.

Mesmo que inicialmente exista apenas um usuário, as consultas e
operações devem respeitar o identificador do usuário autenticado.

### 6.2. Conversations

Responsável pelo ciclo de vida das conversas e mensagens.

Escopo inicial:

-   Criar conversa.
-   Listar conversas.
-   Consultar conversa.
-   Excluir conversa.
-   Registrar mensagens do usuário.
-   Registrar respostas do assistente.
-   Consultar histórico de mensagens.
-   Controlar ordenação e paginação.

O histórico persistido é a fonte de verdade das mensagens. Ele não deve
ser confundido com memória de longo prazo.

### 6.3. Assistant

Responsável por coordenar a interação conversacional.

Fluxo esperado:

1.  Receber uma solicitação validada.
2.  Recuperar o histórico/contexto necessário.
3.  Solicitar a geração ao LLM Gateway.
4.  Encaminhar os eventos de streaming ao cliente.
5.  Consolidar e persistir a resposta final.
6.  Tratar falhas, cancelamentos e encerramento da geração.

Inicialmente haverá um único agente conversacional, sem handoffs ou
arquitetura multiagente.

### 6.4. Context

Responsável por preparar o contexto enviado ao modelo.

No primeiro MVP, o contexto será limitado a:

-   System Instructions.
-   Mensagens recentes da conversa.
-   Resumo da conversa, quando implementado e necessário.

O módulo deve expor uma abstração para construção do contexto, evitando
que o Assistant conheça os detalhes de como o contexto é recuperado.

Interface conceitual:

``` python
class ContextProvider:
    async def build_context(
        self,
        conversation_id: str,
        user_id: str
    ):
        ...
```

Implementação inicial:

``` text
ContextProvider
    |
    v
ConversationContextProvider
    |
    +-- System Instructions
    +-- Recent Messages
    +-- Conversation Summary (fase posterior)
```

A interface deve permitir adicionar futuramente:

-   Profile Memory.
-   Episodic Memory.
-   Knowledge Memory.
-   Documentos recuperados.
-   Preferências persistentes.

Não implementar esses mecanismos no MVP.

------------------------------------------------------------------------

## 7. Experiência conversacional e contexto

### 7.1. Histórico não é memória

É importante manter a distinção:

  -----------------------------------------------------------------------
  Histórico de conversa               Memória de longo prazo
  ----------------------------------- -----------------------------------
  Registra mensagens trocadas         Registra informações relevantes
                                      sobre o usuário

  Pertence a uma conversa             Pode ser compartilhada entre
                                      conversas

  Recuperação cronológica             Recuperação por relevância e
                                      contexto

  Faz parte do MVP                    Fase futura
  -----------------------------------------------------------------------

O histórico deve ser persistido desde o início. A memória de longo prazo
será adicionada posteriormente, sem alterar a responsabilidade do módulo
Conversations.

### 7.2. Estratégia de contexto inicial

Para preservar a qualidade da conversa sem implementar memória:

1.  Incluir as instruções do sistema.
2.  Recuperar mensagens recentes da conversa atual.
3.  Incluir um resumo da conversa quando essa funcionalidade estiver
    disponível.
4.  Controlar o orçamento de tokens.
5.  Evitar enviar todo o histórico indiscriminadamente.

O resumo deve complementar, e não substituir, o histórico original. Deve
ser possível reconstruir o contexto a partir das mensagens persistidas.

### 7.3. System Instructions

As instruções do sistema devem definir:

-   Identidade e papel do assistente.
-   Tom e estilo de comunicação.
-   Comportamento diante de dúvidas.
-   Limites de atuação.
-   Regras de segurança.
-   Como lidar com informações insuficientes.

As instruções devem ser centralizadas e versionadas, evitando sua
duplicação em diferentes partes do código.

------------------------------------------------------------------------

## 8. Streaming

Streaming faz parte do primeiro MVP.

A resposta deve ser exibida progressivamente, conforme o modelo a gera,
em vez de aguardar a conclusão integral da geração.

### Fluxo

``` text
React
  |
  | POST /messages/stream
  v
FastAPI
  |
  | Streaming request
  v
OpenAI API
  |
  | Text deltas / events
  v
FastAPI
  |
  | SSE events
  v
React
  |
  v
Atualização progressiva da mensagem
```

### Diretrizes

-   Utilizar Server-Sent Events (SSE) inicialmente.
-   Padronizar os tipos de evento enviados ao frontend.
-   Diferenciar conteúdo textual, conclusão e erro.
-   Tratar desconexão do cliente e cancelamento da geração.
-   Persistir a mensagem final consolidada.
-   Evitar persistir cada fragmento individualmente.
-   Garantir que falhas não deixem mensagens em estado inconsistente.

O contrato de streaming deve ser documentado separadamente, pois eventos
SSE não são representados da mesma forma que operações HTTP
convencionais no OpenAPI.

------------------------------------------------------------------------

## 9. Contratos iniciais da API

Todos os endpoints devem utilizar o prefixo `/api/v1`.

Proposta inicial:

  ----------------------------------------------------------------------------------------------------
  Método                  Endpoint                                             Responsabilidade
  ----------------------- ---------------------------------------------------- -----------------------
  POST                    `/users`                                             Criar usuário, se o
                                                                               cadastro fizer parte do
                                                                               fluxo inicial

  POST                    `/auth/login`                                        Autenticar usuário

  POST                    `/conversations`                                     Criar conversa

  GET                     `/conversations`                                     Listar conversas

  GET                     `/conversations/{conversation_id}`                   Consultar conversa

  DELETE                  `/conversations/{conversation_id}`                   Excluir conversa

  GET                     `/conversations/{conversation_id}/messages`          Listar mensagens

  POST                    `/conversations/{conversation_id}/messages/stream`   Enviar mensagem e
                                                                               receber resposta via
                                                                               SSE
  ----------------------------------------------------------------------------------------------------

A lista é uma proposta inicial, não um contrato fechado. Os schemas,
códigos de status, paginação, autenticação e eventos SSE devem ser
detalhados antes da implementação de cada endpoint.

### Diretrizes de API

-   Utilizar schemas de request e response específicos.
-   Padronizar erros com códigos e mensagens previsíveis.
-   Validar autorização em todas as operações por identificador.
-   Implementar paginação no histórico.
-   Não expor informações internas ou segredos nos erros.
-   Não permitir acesso a conversas pertencentes a outro usuário.
-   Documentar exemplos de requests e responses.

------------------------------------------------------------------------

## 10. LLM Gateway

O acesso à OpenAI deve ficar isolado em uma camada de integração.

Responsabilidades:

-   Encapsular o SDK da OpenAI.
-   Centralizar seleção de modelo.
-   Controlar timeout e tratamento de erros.
-   Implementar streaming.
-   Registrar metadados operacionais.
-   Controlar uso de tokens e custos.
-   Permitir futura substituição ou adição de provedores.

Interface conceitual:

``` python
class LLMProvider:
    async def generate(self, messages, **options):
        ...

    async def stream(self, messages, **options):
        ...
```

A implementação inicial utilizará a OpenAI API. Não criar uma abstração
genérica excessiva: a interface deve refletir os casos de uso reais da
aplicação.

------------------------------------------------------------------------

## 11. Segurança e privacidade

Mesmo no ambiente local, implementar boas práticas desde o início:

-   Segredos armazenados em variáveis de ambiente.
-   Arquivo `.env` fora do controle de versão.
-   `.env.example` sem credenciais reais.
-   Autenticação e autorização no backend.
-   Isolamento de conversas e mensagens por usuário.
-   Validação de entradas.
-   Limites de tamanho das mensagens.
-   Tratamento seguro de erros.
-   Logs sem conteúdo sensível desnecessário.
-   Dependências atualizadas e versionadas.

### Uso da OpenAI API

As mensagens e o contexto enviados ao modelo são transmitidos à
infraestrutura da OpenAI. Portanto, a aplicação não deve afirmar que
todo o processamento ocorre localmente.

Enviar somente o contexto necessário e consultar as políticas e
configurações de retenção aplicáveis à API.

------------------------------------------------------------------------

## 12. Infraestrutura e execução local

A primeira versão será executada localmente.

Utilizar Docker Compose para facilitar a inicialização dos componentes:

-   Frontend.
-   Backend.
-   PostgreSQL.

Não implementar AWS nesta etapa.

Também não adicionar inicialmente:

-   Redis.
-   SQS ou outros brokers.
-   S3.
-   pgvector.
-   Kubernetes.
-   Microserviços.
-   Serviços de observabilidade distribuída.

A infraestrutura poderá evoluir quando houver necessidade concreta, sem
condicionar a arquitetura de domínio a um provedor específico.

------------------------------------------------------------------------

## 13. Roadmap de implementação

### P0 --- Foundation

Objetivo: preparar a estrutura e validar a comunicação entre os
componentes.

Entregas:

-   Criar repositório e estrutura inicial.
-   Configurar FastAPI.
-   Configurar React + TypeScript.
-   Configurar PostgreSQL local.
-   Configurar SQLAlchemy e Alembic.
-   Configurar Docker Compose.
-   Definir estrutura modular por domínio.
-   Configurar OpenAPI.
-   Criar health check.
-   Configurar variáveis de ambiente.

Critério de conclusão: frontend, backend e banco executam localmente e
se comunicam corretamente.

### P1 --- Conversational Experience

Objetivo: entregar uma experiência conversacional funcional.

Entregas:

-   Autenticação.
-   Criação e listagem de conversas.
-   Persistência de mensagens.
-   Integração com OpenAI via LLM Gateway.
-   Envio e recebimento de mensagens.
-   Streaming via SSE.
-   Histórico de mensagens.
-   Interface de chat.
-   Tratamento de erros e cancelamentos.

Critério de conclusão: usuário consegue iniciar uma conversa, enviar
mensagens, acompanhar respostas via streaming e recuperar o histórico
após reiniciar a aplicação.

### P2 --- Context Management

Objetivo: melhorar a continuidade e a qualidade das conversas.

Entregas:

-   ContextProvider.
-   System Instructions centralizadas.
-   Estratégia de recuperação de mensagens recentes.
-   Controle de orçamento de tokens.
-   Conversation Summary, se necessário.
-   Testes de continuidade contextual.

Critério de conclusão: o assistente mantém coerência dentro de conversas
longas sem depender do envio integral do histórico.

### P3 --- Memory e Research

Objetivo: ampliar a capacidade do assistente.

Possíveis entregas:

-   Profile Memory.
-   Episodic Memory.
-   Knowledge Memory.
-   PostgreSQL + pgvector.
-   Extração e recuperação de memórias.
-   Interface de edição e exclusão de memórias.
-   Pesquisa na web.
-   Recuperação de páginas e citações.

### P4 --- Personalization e Evaluation

Objetivo: melhorar a qualidade e a personalização.

Possíveis entregas:

-   Preferências configuráveis.
-   Contexto adaptativo.
-   Evals para qualidade conversacional.
-   Avaliação da recuperação de memória.
-   Métricas de latência e custo.
-   Observabilidade.

### P5 --- Expansion

Objetivo: expandir os canais e capacidades do assistente.

Possíveis entregas:

-   Tool Registry.
-   Integrações externas.
-   Aprovação humana para ações sensíveis.
-   Interface de voz.
-   Integração com Alexa.
-   Aplicativos e outros canais.
-   Avaliação de deploy em AWS.

------------------------------------------------------------------------

## 14. Avaliação e qualidade

A qualidade deve ser acompanhada desde o primeiro MVP, ainda que com
instrumentação simples.

Indicadores iniciais:

-   Latência até o primeiro fragmento da resposta (time to first token).
-   Tempo total de geração.
-   Taxa de sucesso das requisições.
-   Erros de integração com o LLM.
-   Tokens utilizados por interação.
-   Custo estimado por interação.
-   Continuidade contextual em conversas longas.

Criar testes automatizados para cenários como:

-   Criar e recuperar uma conversa.
-   Persistir mensagens na ordem correta.
-   Isolar conversas por usuário.
-   Processar uma resposta via streaming.
-   Lidar com falha do provedor.
-   Recuperar contexto recente.
-   Evitar perda de mensagens em desconexões.

------------------------------------------------------------------------

## 15. Fora do escopo do primeiro MVP

Para preservar simplicidade e foco, não implementar inicialmente:

-   Memória de longo prazo.
-   Busca vetorial.
-   Pesquisa na web.
-   Upload e processamento de documentos.
-   Multiagentes.
-   Execução de código ou shell.
-   Ações autônomas em serviços externos.
-   Integrações com Google, Microsoft ou outros serviços.
-   Interface de voz.
-   Integração com Alexa.
-   Infraestrutura AWS.
-   Microserviços.
-   Filas e processamento assíncrono distribuído.

Esses itens devem ser considerados somente nas fases futuras.

------------------------------------------------------------------------

## 16. Critérios de sucesso do primeiro MVP

O primeiro MVP será considerado funcional quando:

1.  A aplicação executar localmente de forma reproduzível.
2.  O usuário conseguir se autenticar.
3.  O usuário conseguir criar e gerenciar conversas.
4.  As mensagens forem persistidas corretamente.
5.  O assistente responder utilizando a OpenAI API.
6.  As respostas forem exibidas via streaming.
7.  O histórico puder ser recuperado após reiniciar a aplicação.
8.  O contexto recente for mantido dentro de uma conversa.
9.  O frontend consumir exclusivamente os contratos da API.
10. Os módulos mantiverem seus limites e responsabilidades.

------------------------------------------------------------------------

## 17. Diretrizes para implementação

-   Implementar uma fase por vez.
-   Não antecipar funcionalidades de fases futuras.
-   Revisar decisões arquiteturais quando surgirem necessidades reais.
-   Priorizar clareza e simplicidade sobre abstrações prematuras.
-   Manter contratos da API documentados.
-   Escrever testes para regras e casos de uso importantes.
-   Evitar dependências circulares entre módulos.
-   Não permitir acesso direto às tabelas de outro módulo.
-   Manter integrações externas atrás de interfaces.
-   Atualizar este documento quando decisões relevantes forem alteradas.

## Visão final

Construir primeiro um núcleo conversacional independente de canais, com
API First e monólito modular orientado a domínios funcionais.

O primeiro objetivo não é criar um agente altamente autônomo, mas
entregar uma experiência conversacional confiável, contextualizada e
extensível.

A memória, pesquisa, ferramentas, voz e integrações serão adicionadas
gradualmente, preservando os limites arquiteturais estabelecidos desde o
início.
