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

## Critérios de aceite / definição de pronto

- [ ] Toda resposta do backend inclui os quatro cabeçalhos de
      segurança listados acima.
- [ ] Uma requisição de escrita sem o cabeçalho `X-Portal-Client` é
      rejeitada com `403`, mesmo com um cookie de sessão válido.
- [ ] O frontend envia o cabeçalho em toda chamada — nenhuma
      funcionalidade existente quebra.
- [ ] Auditoria documentada confirma que as permissões reais da GitHub
      App e da OAuth App não excedem o teto da ADR-0004.
- [ ] Nenhuma resposta de erro em produção (`cookie_secure`/produção)
      vaza detalhe interno além de `{error, message, correlation_id}`.
- [ ] `ruff check`, `pytest`, `eslint`, `vue-tsc` e `vitest` passam;
      `npm run build` gera bundle sem erro.

## Riscos técnicos e decisões de arquitetura

Ver [ADR-0014](decisions/0014-csrf-cookies-cross-origin.md) para a
decisão completa do mecanismo de CSRF.

- **Cabeçalho customizado quebrando algum cliente não-navegador**:
  aceito — nenhum cliente assim existe ou está planejado (ver
  consequências da ADR-0014).
- **CSP quebrando alguma funcionalidade do próprio portal** (ex.: se o
  Tiptap ou alguma dependência exigir `unsafe-inline`): a política
  exata precisa ser calibrada e testada manualmente contra a aplicação
  real antes de fechar esta sub-fase, não só copiada de um template
  genérico.

## Roteiro de validação manual (Fase 4.4.5)

A ser executado e registrado quando a implementação estiver concluída:

- [ ] Inspecionar os cabeçalhos de uma resposta real (`curl -I`) e
      confirmar os quatro cabeçalhos de segurança.
- [ ] Tentar enviar uma submissão sem o cabeçalho `X-Portal-Client`
      (ex.: via `curl`, fora do frontend) → rejeitada com `403`.
- [ ] Usar o portal normalmente pelo navegador (login, edição, envio)
      → nenhuma funcionalidade quebrada pelo CSP ou pelo novo
      cabeçalho.
- [ ] Revisar, via `gh api`, as permissões reais instaladas da GitHub
      App e da OAuth App, e confirmar que batem com o documentado.

## Dependências

- Nenhuma dependência de código das demais sub-fases — pode ser
  implementada isoladamente.
