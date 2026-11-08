# 0003 — Client gerado versionado

**Status:** aceita

## Contexto

Os tipos do frontend são gerados a partir do contrato. Eles podem ser gerados no build ou
versionados no repositório.

## Decisão

Versionar `apps/frontend/src/services/api/generated/`. O CI regenera os tipos e falha se
houver diferença.

## Consequências

- Mudanças no contrato aparecem no diff do PR também do lado do frontend.
- O build não depende do diretório `contracts/` (útil no build Docker do frontend).
- Quem alterar o contrato precisa rodar `make generate-client` antes do commit.
