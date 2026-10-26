# ADR-0014: Mitigação de CSRF para cookies de sessão cross-origin

## Status

Aceita

## Contexto

Em produção, o frontend (GitHub Pages) e o backend (API Gateway) vivem
em origens diferentes. Para o cookie de sessão ser enviado nas
requisições do frontend, ele precisa de `SameSite=None`
(`cookie_samesite` já é `"none"` em produção no template SAM) — mas
`SameSite=None` desativa exatamente a proteção nativa do navegador
contra CSRF que `Lax`/`Strict` dariam. A proteção CSRF que já existe
(`auth/oauth_state.py`) cobre só o handshake de login (o parâmetro
`state` do OAuth); não protege `POST /api/submissions` (nem qualquer
futura rota de escrita) depois que a sessão já existe.

## Decisão

Exigir um cabeçalho customizado (`X-Portal-Client: 1`) em toda
requisição que altera estado (`POST`, e qualquer `PUT`/`DELETE`
futuro), verificado por um middleware do backend que rejeita a
requisição com `403` se o cabeçalho estiver ausente — mesmo com um
cookie de sessão válido.

Funciona porque:
- o frontend já pode enviar esse cabeçalho trivialmente em toda
  chamada `fetch`;
- uma requisição forjada por um site malicioso (formulário cross-site,
  `<img>`, etc.) não consegue definir um cabeçalho customizado sem
  disparar um preflight CORS — e a política de CORS já configurada
  (`AllowOrigins: [FrontendUrl]`, um único valor) rejeita preflights de
  qualquer origem que não seja o próprio frontend do portal.

Não exige armazenamento de token no servidor nem o padrão
double-submit-cookie — coerente com a postura sem banco de dados do
MVP.

## Consequências

- Complementa (não substitui) a proteção CSRF já existente no
  handshake OAuth — cada uma protege uma parte diferente do fluxo.
- A configuração de CORS em `infra/sam/template.yaml`
  (`AllowOrigins: [FrontendUrl]`) passa a ser um controle de
  **segurança**, não só de conveniência — nunca deve ser ampliada para
  `*` ou múltiplas origens sem revisitar esta ADR.
- Qualquer cliente futuro que não seja o frontend do portal (ex.: uma
  CLI) precisaria enviar o mesmo cabeçalho explicitamente — aceitável,
  já que nenhum cliente assim existe ou está planejado no MVP.

## Referências

- [docs/initial-architecture.md](../initial-architecture.md) — seção 14.
- `backend/src/auth/oauth_state.py` — proteção CSRF do handshake OAuth
  (decisão anterior, não alterada por esta ADR).
- [docs/phase-4.4-plan.md](../phase-4.4-plan.md).
