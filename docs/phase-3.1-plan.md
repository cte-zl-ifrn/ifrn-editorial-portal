# Plano da Fase 3.1 — Escrita de um documento, sem assets

Sub-fase de [docs/phase-3-plan.md](phase-3-plan.md). Desdobramento da
[issue #12](https://github.com/cte-zl-ifrn/ifrn-editorial-portal/issues/12).

## Objetivo

A partir do corpo editado no Tiptap e já serializado para Markdown (Fase
2.2), criar uma branch derivada de `main`, gravar apenas o arquivo
Markdown alterado (front matter re-lido no momento da gravação + corpo
serializado) e abrir um Pull Request contra `main` no `central-ajuda` —
sem upload de imagens ou arquivos.

## Escopo

### Dentro

- Backend: endpoint `POST /api/submissions`, exigindo sessão válida e
  usuário autorizado (mesmo modelo já usado para leitura).
- Backend: revalidação de conflito — reler o documento no momento da
  gravação e comparar seu `sha` com o `base_sha` enviado pelo cliente;
  divergência retorna `409` sem gravar nada.
- Backend: criação de branch a partir do `sha` atual de `main`, no
  formato `portal/update/{ano}/{id}-{slug}` (seção 8.3 do documento de
  arquitetura).
- Backend: gravação do arquivo via Contents API
  (`front_matter_raw` recém-lido + `body` enviado pelo cliente), na
  branch criada.
- Backend: criação do Pull Request contra `main`, com o modelo de corpo
  já especificado (seção 8.4 do documento de arquitetura): resumo,
  autor, data, arquivos alterados, checklist de validações.
- Backend: resposta síncrona com o identificador da submissão, nome da
  branch e dados do Pull Request (número e URL).
- Frontend: botão "Enviar alteração" na view de edição, solicitando um
  resumo/justificativa antes de enviar; exibição do resultado (link do
  PR) ou do erro (incluindo conflito, com opção de recarregar o
  documento).
- Atualizar `docs/api/openapi.yaml` com o novo endpoint.

### Fora

- Upload de imagens ou arquivos (Fase 3.2).
- Escolha de caminho pelo usuário ou criação de novo documento — o
  caminho continua fixo (`settings.sample_document_path`).
- Edição de campos do front matter.
- Polling de status do PR após a criação — a resposta síncrona já
  contém o link.
- Idempotência real de submissões repetidas (ver
  [ADR-0011](decisions/0011-escrita-branch-commit-pull-request.md)).
- Qualquer alteração nas regras de autorização já existentes.

## Entregáveis

1. Backend: `github/client.py` estendido com `create_branch`,
   `update_file_content`, `create_pull_request`; novo
   `services/submission_service.py` orquestrando revalidação, branch,
   commit e PR; novo erro `DocumentConflictError` (409).
2. Backend: `handlers/submissions.py` com `POST /api/submissions`.
3. Backend: testes cobrindo sucesso, conflito de `base_sha`, usuário não
   autorizado, e falha de comunicação com o GitHub em cada etapa (branch,
   commit, PR) — cada uma mockada isoladamente.
4. Frontend: ação de envio na view de edição (botão + campo de resumo) e
   estados de resultado (sucesso com link do PR; erro; conflito).
5. `docs/api/openapi.yaml` atualizado com `POST /api/submissions`.

**Entregue** (nomes de arquivo reais): `backend/src/github/client.py`
(+ `get_main_branch_sha`, `create_branch`, `update_file_content`,
`create_pull_request`); `backend/src/services/submission_service.py`;
`backend/src/errors.py:DocumentConflictError`;
`backend/src/models/requests.py:SubmissionRequest`;
`backend/src/models/responses.py:{PullRequestInfo,SubmissionResponse}`;
`backend/src/handlers/submissions.py`; `backend/src/app.py` (registro da
rota + handler de `RequestValidationError` para manter o formato de erro
consistente); `backend/tests/test_submissions.py`.
`frontend/src/services/submissionService.ts`;
`frontend/src/composables/useSubmission.ts`;
`frontend/src/views/HomeView.vue` (formulário de envio + estados de
resultado); `frontend/tests/{useSubmission,submissionService}.spec.ts`.

## Critérios de aceite / definição de pronto

- [x] Um usuário autorizado consegue enviar o corpo editado e receber, na
      resposta, o link de um Pull Request (`handlers/submissions.py` →
      `services/submission_service.py`). Confirmado com mocks; a criação
      de um PR real contra o `central-ajuda` fica para a Fase 3.1.5.
- [x] O Pull Request contém: título objetivo, resumo informado pelo
      usuário, autor (login do GitHub), data/hora, arquivo alterado, e o
      checklist de validações do modelo já especificado
      (`_build_pull_request_body`).
- [x] A branch criada segue o formato `portal/update/{ano}/{id}-{slug}` e
      é derivada do `sha` atual de `main` no momento da submissão
      (`get_main_branch_sha` + `create_branch`).
- [x] O arquivo gravado é `front_matter_raw` (relido no momento da
      gravação via `split_front_matter`) + `body` (enviado pelo
      cliente) — nunca uma reserialização do front matter, nunca o front
      matter enviado pelo cliente (que nem é aceito pelo
      `SubmissionRequest`).
- [x] Se o documento mudou no GitHub desde que o usuário começou a
      editar (`base_sha` divergente), a submissão é rejeitada com `409`
      (`DocumentConflictError`), sem criar branch, commit ou PR —
      testado explicitamente checando que as rotas de escrita mockadas
      não foram chamadas.
- [x] Usuário não autorizado recebe `403` e não consegue submeter nada.
- [x] `owner`, `repo` e a branch base (`main`) continuam fixos no
      backend — `SubmissionRequest` não declara esses campos; um teste
      confirma que enviá-los mesmo assim não tem efeito.
- [x] Nenhuma permissão além de `Contents: Read and write` e
      `Pull requests: Read and write` é usada (mesmas chamadas de leitura
      já existentes + Contents API para escrita + API de refs/pulls).
- [x] Testes automatizados cobrem sucesso, conflito, autorização
      (401/403), validação (422 para corpo/resumo vazios), e falha em
      cada chamada ao GitHub (branch/commit/PR), todas mockadas — 10
      testes novos em `backend/tests/test_submissions.py` (41 no total
      no backend).
- [x] `ruff check`, `pytest`, `eslint`, `vue-tsc` e `vitest` passam;
      `npm run build` gera bundle de produção sem erro.
- [x] `docs/api/openapi.yaml` reflete o novo endpoint.

## Riscos técnicos e decisões de arquitetura

Ver [ADR-0011](decisions/0011-escrita-branch-commit-pull-request.md) para
o mecanismo de gravação, revalidação de conflito e postura de
idempotência. Riscos específicos desta sub-fase:

- **Permissão da GitHub App insuficiente ou excessiva**: a instalação
  real precisa ser atualizada (fora do código) para `Contents: Read and
  write` e `Pull requests: Read and write` antes desta fase poder ser
  validada de ponta a ponta contra o GitHub real — ver "Dependências"
  abaixo. O código nunca solicita nem usa permissão além dessas duas.
- **Falha parcial** (branch criada, mas commit ou PR falham): o backend
  deve tratar cada etapa com seu próprio erro claro; uma branch órfã sem
  PR associado é um efeito colateral aceitável de uma falha nesta fase
  (não requer rollback automático), mas deve ser logada com
  `correlation_id` para permitir limpeza manual.
- **Slug do documento de demonstração**: derivado do nome do arquivo
  (`como-fazer-cursos`), não de um campo do front matter — mantém
  consistência com o caminho fixo já usado nas fases anteriores.

## Roteiro de validação manual (Fase 3.1.5)

Executado e registrado em
[docs/phase-3.1.5-manual-validation.md](phase-3.1.5-manual-validation.md)
(2026-08-26):

- [x] Login com usuário autorizado → editar o documento → enviar → PR
      real criado no `central-ajuda`
      ([#1](https://github.com/cte-zl-ifrn/central-ajuda/pull/1)), com
      corpo, autor e checklist corretos.
- [x] Conflito: alterar o arquivo diretamente no GitHub entre o
      carregamento e o envio → submissão rejeitada com erro de conflito,
      nenhum branch/commit/PR criado.
- [x] Usuário sem permissão → tentativa de envio rejeitada, sem criar
      nada no `central-ajuda`.
- [x] Inspeção do Pull Request criado confirma que nenhuma permissão
      além de `Contents` e `Pull requests` foi necessária.
- [x] Um dos Pull Requests de teste foi revisado e **mergeado de
      verdade** no `central-ajuda` — autorizado explicitamente pelo
      mantenedor (issue #12). Confirmado, via API, que o conteúdo em
      `main` reflete exatamente a edição feita e que nada além do
      arquivo esperado foi modificado.

## Dependências

- Fase 2.1 e Fase 2.2 concluídas e validadas (parser, serializer, prévia
  local já funcionando).
- ~~Ação operacional, fora do código: atualizar a instalação da GitHub App
  em `cte-zl-ifrn/central-ajuda` para incluir `Contents: Read and write` e
  `Pull requests: Read and write`~~ — **concluída** (confirmado pelo
  mantenedor na [issue #12](https://github.com/cte-zl-ifrn/ifrn-editorial-portal/issues/12):
  `Contents: Read and write`, `Pull requests: Read and write`,
  `Metadata: Read-only`, acesso restrito a `cte-zl-ifrn/central-ajuda`).
- Confirmação explícita de que é aceitável abrir Pull Requests de teste
  no `central-ajuda` durante a validação manual — **concedida**, incluindo
  merge real de um deles (ver roteiro acima).

## Decisões tomadas durante a implementação

- Resumo/justificativa é obrigatório no frontend (`SubmissionRequest.summary`
  exige pelo menos 1 caractere; o botão de envio fica desabilitado até o
  campo ser preenchido).
- Identificador de submissão: `secrets.token_hex(4)` (8 caracteres
  hexadecimais) — simples e suficientemente único para o volume desta
  fase, sem exigir uma ADR própria.
- Handler global de `RequestValidationError` adicionado a `app.py` para
  que erros de validação do Pydantic (corpo/resumo vazios) respondam no
  mesmo formato `{error, message, correlation_id}` dos demais erros da
  API, em vez do formato padrão do FastAPI.
