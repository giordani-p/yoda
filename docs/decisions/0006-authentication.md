# 0006 — Autenticação por JWT em cookie HttpOnly

**Status:** aceita

## Contexto

O Yoda é um assistente pessoal, com poucos usuários e sem cadastro público, mas toda operação
precisa respeitar o usuário autenticado. Pelo ADR 0004 nenhum módulo importa `users`, então a
identificação do usuário na requisição precisa funcionar sem consultar dados desse módulo.

## Decisão

- Login por e-mail e senha (`POST /api/v1/auth/login`). Senhas com hash argon2 (`pwdlib`). O
  e-mail é normalizado (minúsculas, sem espaços) no cadastro e no login. Quando o e-mail não
  existe, um hash fictício é verificado para que o tempo de resposta não revele isso.
- A sessão é um JWT HS256 (`PyJWT`) com `sub` (id do usuário), `iat` e `exp`, num cookie
  `yoda_session` com `HttpOnly`, `SameSite=Lax`, `Path=/` e `Secure` configurável. Validade de
  7 dias (`AUTH_TOKEN_TTL_HOURS`), sem refresh token.
- `app/shared/security/` emite e verifica o token sem acessar o banco e expõe a dependência
  `CurrentUserId`. Sem sessão válida, a resposta é 401 `UNAUTHENTICATED`.
- `AUTH_SECRET_KEY` precisa ter ao menos 32 caracteres. Em `APP_ENV=development` existe uma
  chave fixa de desenvolvimento; nos demais ambientes a aplicação não sobe sem uma chave própria.
- Usuários são criados só pelo terminal (`make create-user`), sem endpoint de cadastro. Senha com
  ao menos 8 caracteres.
- O CORS permite credenciais para as origens configuradas, e o frontend envia
  `credentials: "include"`.

## Consequências

- O token não fica acessível ao JavaScript, o que reduz o impacto de um XSS.
- Logout apaga o cookie, mas um token copiado continua válido até expirar. Revogação exigiria
  estado no servidor; reavaliar se surgir necessidade.
- Um usuário removido do banco com token válido recebe 401 em `/users/me`; as demais rotas
  precisam tratar o caso quando dependerem dos dados do usuário.
- `SameSite=Lax` cobre CSRF nas requisições entre sites. Frontend e backend em portas diferentes
  de `localhost` contam como o mesmo site.
- Em produção com HTTPS, configurar `AUTH_COOKIE_SECURE=true`.
