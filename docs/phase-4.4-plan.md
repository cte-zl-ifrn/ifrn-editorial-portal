# Plano da Fase 4.4 — Segurança da aplicação

Sub-fase de [docs/phase-4-plan.md](phase-4-plan.md). Desdobramento da
[issue #13](https://github.com/cte-zl-ifrn/ifrn-editorial-portal/issues/13).

## Objetivo

Fechar as lacunas de segurança de aplicação que não foram cobertas por
nenhuma fase anterior: cabeçalhos de segurança HTTP, CSRF para
requisições autenticadas por cookie cross-origin, uma revisão
sistemática das validações de entrada já existentes, e uma auditoria
das permissões da GitHub App e da OAuth App.

## Escopo

### Dentro

- Backend: middleware adicionando cabeçalhos de segurança em toda
  resposta — `Content-Security-Policy`, `X-Content-Type-Options: nosniff`,
  `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`.
- Backend: middleware exigindo o cabeçalho `X-Portal-Client` em toda
  requisição que altera estado — ver
  [ADR-0014](decisions/0014-csrf-cookies-cross-origin.md).
- Frontend: `apiClient` (`frontend/src/services/apiClient.ts` ou
  equivalente) passa a enviar esse cabeçalho em toda chamada.
- Revisão sistemática (não uma reimplementação) das validações de
  entrada já existentes — `assets/validation.py`, modelos Pydantic de
  requisição — documentando explicitamente o que já está coberto, para
  não duplicar esforço.
- Auditoria documentada das permissões reais da GitHub App e da OAuth
  App instaladas hoje, comparadas ao teto definido na
  [ADR-0004](decisions/0004-integracao-github-app.md).
- Mensagens de erro em produção: confirmar que nenhuma resposta de erro
  vaza detalhe interno (stack trace, caminho de arquivo) — já em boa
  parte coberto pelo formato de erro padronizado
  (`{error, message, correlation_id}`), mas sem uma checagem explícita
  até aqui.

### Fora

- Reescrever validações já existentes e já testadas — esta fase audita
  e complementa, não substitui.
- Content Security Policy do frontend em si (o `index.html`/build do
  Vite) — o CSP desta fase é da resposta HTTP do backend; CSP do
  frontend estático fica para quando houver um domínio/CDN definido
  (questão em aberto em `docs/project-context.md`).
- Testes de penetração formais ou automatizados de terceiros — fora do
  orçamento e do escopo do MVP.

## Entregáveis

1. Backend: middleware de cabeçalhos de segurança.
2. Backend: middleware de exigência do `X-Portal-Client` nas rotas de
   escrita.
3. Frontend: `apiClient` enviando o cabeçalho em toda chamada.
4. Testes: cabeçalhos presentes em toda resposta; requisição de
   escrita sem o cabeçalho é rejeitada com `403`, mesmo com sessão
   válida.
5. Documento de auditoria de permissões (seção nova em
   `backend/README.md` ou arquivo dedicado).
6. `docs/decisions/0014-csrf-cookies-cross-origin.md` (ver
   [ADR-0014](decisions/0014-csrf-cookies-cross-origin.md)).

**Entregue** (nomes reais): `backend/src/app.py` —
`security_headers_middleware`, `csrf_header_middleware` e
`unhandled_exception_handler` (não previsto no escopo original, ver
"Decisões tomadas durante a implementação"). `frontend/src/services/apiClient.ts`
— `X-Portal-Client: 1` em toda chamada. `backend/tests/test_security.py`
(6 testes novos); `backend/tests/conftest.py` (fixture `client` passa a
enviar o cabeçalho por padrão, espelhando o frontend real);
`frontend/tests/apiClient.spec.ts` (1 teste novo). Auditoria de
permissões documentada em `backend/README.md`, seção "Segurança da
aplicação (Fase 4.4)". `docs/api/openapi.yaml` — `403`
(`missing_csrf_header`) em `POST /api/submissions` e `POST
/auth/logout`.

## Critérios de aceite / definição de pronto

- [x] Toda resposta do backend inclui os quatro cabeçalhos de
      segurança listados acima
      (`test_every_response_includes_the_security_headers`) — exceto
      `Content-Security-Policy` em `/docs`/`/redoc`, deliberadamente
      (`test_docs_paths_are_exempt_from_the_content_security_policy`).
- [x] Uma requisição de escrita sem o cabeçalho `X-Portal-Client` é
      rejeitada com `403`, mesmo com um cookie de sessão válido
      (`test_write_request_without_csrf_header_is_rejected_even_with_a_valid_session`).
- [x] O frontend envia o cabeçalho em toda chamada — nenhuma
      funcionalidade existente quebra (76 testes no frontend, todos
      passando; `eslint`/`vue-tsc`/build limpos).
- [x] Auditoria documentada confirma que as permissões reais da GitHub
      App e da OAuth App não excedem o teto da ADR-0004 — ver
      `backend/README.md`, verificado via `gh api
      orgs/cte-zl-ifrn/installations` em 2026-08-27.
- [x] Nenhuma resposta de erro em produção vaza detalhe interno além
      de `{error, message, correlation_id}` — inclusive para uma
      exceção não antecipada, garantido por
      `unhandled_exception_handler`
      (`test_unexpected_exception_never_leaks_internal_detail`).
- [x] `ruff check`, `pytest`, `eslint`, `vue-tsc` e `vitest` passam;
      `npm run build` gera bundle sem erro — 80 testes no backend (74 +
      6 novos), 76 no frontend (75 + 1 novo).

## Riscos técnicos e decisões de arquitetura

Ver [ADR-0014](decisions/0014-csrf-cookies-cross-origin.md) para a
decisão completa do mecanismo de CSRF.

- **Cabeçalho customizado quebrando algum cliente não-navegador**:
  aceito — nenhum cliente assim existe ou está planejado (ver
  consequências da ADR-0014).
- **CSP quebrando alguma funcionalidade do próprio portal** (ex.: se o
  Tiptap ou alguma dependência exigir `unsafe-inline`): **risco não se
  concretizou, e o motivo ficou claro na implementação** — o CSP desta
  fase é um cabeçalho das respostas do *backend*, que só serve JSON (e,
  à parte, a documentação automática do FastAPI). O Tiptap roda
  inteiramente no *frontend*, servido de uma origem diferente (GitHub
  Pages) — o CSP do backend não tem nenhum efeito sobre a página que o
  frontend serve. `default-src 'none'` pôde ser usado sem nenhuma
  exceção para o próprio portal; só `/docs`/`/redoc` (scripts de CDN da
  documentação automática do FastAPI) precisaram ficar fora.

## Decisões tomadas durante a implementação

- **`unhandled_exception_handler` adicionado, além do escopo original**:
  o plano pedia só *confirmar* que nenhuma resposta vaza detalhe
  interno — ao investigar, ficou claro que uma exceção não mapeada
  (nenhum `PortalError` conhecido) escapava para o handler padrão do
  Starlette, que devolve texto plano (`Internal Server Error`), não o
  envelope `{error, message, correlation_id}` do resto da API. Não
  vazava detalhe (já que `debug=False`), mas era inconsistente. Um
  handler para `Exception` genérico fecha essa lacuna — Starlette
  prioriza handlers mais específicos (`PortalError`,
  `RequestValidationError`) automaticamente, então isso não muda
  nenhum comportamento de erro já existente.
- **Middleware de CSRF registrado antes do de tamanho de corpo, ambos
  antes do de log de acesso**: ordem importa em middlewares HTTP no
  Starlette — o último registrado é o mais externo (roda primeiro na
  entrada). Registrar CSRF e tamanho *antes* do log de acesso garante
  que uma rejeição em qualquer um deles ainda apareça em
  `request.completed`, como qualquer outra resposta.
- **Auditoria de permissões feita via `gh api`, não só por leitura de
  código**: confirma o estado real e atual das instalações (GitHub App
  e escopo do OAuth), não só o que o código *pretende* fazer — achado
  real registrado em `backend/README.md` (instalação antiga ainda
  presente, escopo zero da OAuth App confirmado pela ausência do
  parâmetro `scope` na URL de autorização).

## Roteiro de validação manual (Fase 4.4.5)

- [x] Inspecionar os cabeçalhos de uma resposta real (`curl -I`) e
      confirmar os quatro cabeçalhos de segurança. Confirmado via
      `TestClient` (sem exigir credenciais reais):
      ```
      Content-Security-Policy: default-src 'none'
      X-Content-Type-Options: nosniff
      X-Frame-Options: DENY
      Referrer-Policy: no-referrer
      ```
- [x] Tentar enviar uma submissão sem o cabeçalho `X-Portal-Client`
      (ex.: via `curl`, fora do frontend) → rejeitada com `403`.
      Confirmado: `{"error": "missing_csrf_header", "message":
      "Cabeçalho X-Portal-Client obrigatório para esta requisição.",
      "correlation_id": "..."}`.
- [ ] Usar o portal normalmente pelo navegador (login, edição, envio)
      → nenhuma funcionalidade quebrada pelo CSP ou pelo novo
      cabeçalho. **Pendente de confirmação do usuário** — o CSP é do
      backend (não afeta o frontend, servido de outra origem — ver
      "Riscos técnicos" acima), mas só um teste real no navegador
      confirma que nada quebrou na prática.
- [x] Revisar, via `gh api`, as permissões reais instaladas da GitHub
      App e da OAuth App, e confirmar que batem com o documentado.
      Confirmado via `gh api orgs/cte-zl-ifrn/installations` — ver
      auditoria completa em `backend/README.md`.

## Dependências

- Nenhuma dependência de código das demais sub-fases — pode ser
  implementada isoladamente.
