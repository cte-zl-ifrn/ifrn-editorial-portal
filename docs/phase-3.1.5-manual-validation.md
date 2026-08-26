# Fase 3.1.5 — Validação manual

Conclusão operacional da validação manual da Fase 3.1
([docs/phase-3.1-plan.md](phase-3.1-plan.md)): escrita real de um
documento no `central-ajuda` — branch, commit via Contents API e Pull
Request — testado localmente contra o backend e o GitHub reais, com
**merge de verdade** de um dos Pull Requests de teste, autorizado
previamente na [issue #12](https://github.com/cte-zl-ifrn/ifrn-editorial-portal/issues/12).

Data: 2026-08-26

## Resultados

- [x] Login com usuário autorizado → editar → enviar → Pull Request real
      criado no `central-ajuda`:
      [cte-zl-ifrn/central-ajuda#1](https://github.com/cte-zl-ifrn/central-ajuda/pull/1),
      branch `portal/update/2026/f9fdd9f6-como-fazer-cursos`.
- [x] Corpo do Pull Request confirmado (via `gh pr view`): título
      "Atualização: como-fazer-cursos", resumo informado pelo usuário,
      autor `@kelsoncm`, data, arquivo alterado
      (`_docs/proitec/como-fazer-cursos.md`) e checklist de validações no
      formato especificado.
- [x] Apenas o arquivo esperado foi alterado (1 arquivo, +11/-8) — nenhum
      outro arquivo tocado.
- [x] Conflito: alterar o arquivo diretamente no GitHub entre carregar e
      enviar → submissão rejeitada com `409` (`document_conflict`), sem
      criar branch, commit ou PR.
- [x] Usuário sem permissão → tentativa de envio rejeitada, sem criar
      nada no `central-ajuda`.
- [x] Merge real do Pull Request #1 — confirmado via API que o conteúdo
      em `main` reflete exatamente a edição feita no Tiptap (uma palavra
      em itálico) e que o front matter permanece byte-a-byte idêntico ao
      original.

## Observações

- **Achado de configuração, não um bug de código**: ao reautenticar
  depois de trocar `GITHUB_APP_ID` para a nova GitHub App
  (`cte-zl-ifrn-editorial-portal-dev`, com permissão de escrita), o login
  passou a falhar com "This GitHub App must be configured with a
  callback URL" — sintoma de que `GITHUB_OAUTH_CLIENT_ID`/
  `GITHUB_OAUTH_CLIENT_SECRET` (usados para autenticar a *pessoa*, uma
  identidade distinta da GitHub App — ver
  `docs/architecture/authentication-flow.md`) haviam sido trocados, por
  engano, para as credenciais da GitHub App em vez da OAuth App separada
  já usada com sucesso desde a Fase 1.5. Resolvido restaurando as
  credenciais corretas no `.env` local; nenhuma mudança de código foi
  necessária. Documentado em `backend/.env.example` para evitar a mesma
  confusão no futuro.
- A permissão de escrita real usada foi exatamente a prevista: `Contents:
  Read and write` e `Pull requests: Read and write` — nenhuma permissão
  adicional foi solicitada ou usada.

## Efeito nos critérios de aceite da Fase 3.1

Todos os itens do roteiro de validação manual definido em
[docs/phase-3.1-plan.md](phase-3.1-plan.md#roteiro-de-validação-manual-fase-315)
foram confirmados, incluindo o merge real autorizado na issue #12. A
Fase 3.1 está concluída — implementação e validação manual — e a Fase 3
como um todo tem agora seu primeiro caso de escrita real e completa no
`central-ajuda`, do carregamento à publicação.
