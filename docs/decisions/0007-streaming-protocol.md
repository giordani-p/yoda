# 0007 — Protocolo de streaming da resposta (SSE)

**Status:** aceita

## Contexto

As respostas do assistente devem aparecer progressivamente. O protocolo precisa diferenciar
conteúdo, conclusão e erro, tratar desconexões e fazer parte do contrato da API, para que o
frontend use tipos gerados.

## Decisão

- `POST /api/v1/conversations/{conversationId}/messages/stream` responde `text/event-stream`
  com o SSE nativo do FastAPI (`EventSourceResponse`), que também envia pings de keepalive.
- O `data` de cada evento é um JSON `MessageStreamEvent`, união discriminada pelo campo `type`
  e publicada no OpenAPI (`components.schemas`), de onde o frontend gera o tipo:
  `message.user` → zero ou mais `message.delta` → `message.completed` ou `message.error`.
  A linha `event:` do SSE não é usada.
- A mensagem do usuário é validada e gravada numa dependência que roda antes de o stream abrir:
  erros 401, 404 e 422 continuam sendo respostas JSON com o envelope de erro.
- A resposta só é gravada quando concluída (com modelo e tokens). Em falha do provedor, o
  evento `message.error` traz `LLM_PROVIDER_ERROR` (ou `NOT_FOUND`, se a conversa for excluída
  durante a geração, e `INTERNAL_ERROR` para falhas inesperadas) e nada da resposta é gravado.
- Se o cliente desconectar (botão parar, aba fechada), a geração é cancelada, o stream do
  provedor é fechado e nada da resposta é gravado. A mensagem do usuário permanece.
- A transação de leitura do contexto é encerrada antes da geração, para não manter conexão do
  banco ocupada durante o stream.
- O frontend lê o stream com `fetch` (via `openapi-fetch`, `parseAs: "stream"`) e
  `eventsource-parser`, pois o `EventSource` nativo não faz POST.

## Consequências

- Os tipos dos eventos são verificados pelo teste de contrato e gerados no frontend. O
  `openapi-typescript` 7 ignora o `itemSchema` (OpenAPI 3.2) da rota, então o corpo do stream
  aparece como `unknown` e o frontend usa o tipo `MessageStreamEvent` diretamente.
- Uma resposta interrompida não é recuperável depois de recarregar a página.
- Sem retomada de stream (`Last-Event-ID`): uma queda de conexão encerra a resposta.
