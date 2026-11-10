# 0008 — LLM Gateway com a Responses API da OpenAI

**Status:** aceita

## Contexto

O assistente usa a OpenAI, mas a especificação pede que o provedor fique isolado, com seleção de
modelo, timeouts, erros, streaming e uso de tokens centralizados, e sem abstração genérica
excessiva.

## Decisão

- `LLMProvider` (em `app/modules/assistant/llm.py`) tem um único método, `stream(context)`, que
  produz fragmentos (`TextDelta`) e termina com um `Completion` (modelo e tokens), ou levanta
  `LLMProviderError`. Não há `generate` sem streaming enquanto nenhum caso de uso precisar.
- `OpenAIProvider` usa o SDK oficial (`openai`) e a Responses API, com `store=false` (o padrão
  da API é guardar as respostas), `instructions` + mensagens recentes como entrada, esforço de
  raciocínio e limite de tokens de saída configuráveis. Respostas `incomplete`, `failed` e erros
  do SDK viram `LLMProviderError`. O stream é fechado mesmo em cancelamento.
- Configuração por ambiente: `OPENAI_API_KEY`, `OPENAI_MODEL` (desenvolvimento: `gpt-6-luna`;
  produção a definir), `OPENAI_REASONING_EFFORT` (padrão `low`), `OPENAI_MAX_OUTPUT_TOKENS`,
  `OPENAI_TIMEOUT_SECONDS`. Sem chave, a aplicação sobe e o envio responde com erro.
- O contexto vem do módulo `context` (`ContextProvider`): instruções do sistema versionadas em
  `app/modules/context/instructions/<versão>.md` e as últimas `CONTEXT_RECENT_MESSAGES`
  mensagens.
- Logs registram modelo, versão das instruções, tempo até o primeiro fragmento, tempo total e
  tokens, sem o conteúdo das mensagens. Modelo e tokens também são gravados na resposta.
- Os testes usam um provedor falso; nenhum teste chama a OpenAI.

## Consequências

- Trocar ou adicionar um provedor exige só uma nova implementação de `LLMProvider`.
- O esforço de raciocínio afeta a latência percebida; `low` é um ponto de partida a ajustar.
- Respostas cortadas pelo limite de tokens contam como falha (não são gravadas).
