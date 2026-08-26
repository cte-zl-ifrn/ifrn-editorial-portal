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

## Critérios de aceite / definição de pronto

- [ ] Um usuário autorizado consegue enviar o corpo editado e receber, na
      resposta, o link de um Pull Request real aberto no `central-ajuda`.
- [ ] O Pull Request contém: título objetivo, resumo informado pelo
      usuário, autor (login do GitHub), data/hora, arquivo alterado, e o
      checklist de validações do modelo já especificado.
- [ ] A branch criada segue o formato `portal/update/{ano}/{id}-{slug}` e
      é derivada do `sha` atual de `main` no momento da submissão.
- [ ] O arquivo gravado é `front_matter_raw` (relido no momento da
      gravação) + `body` (enviado pelo cliente) — nunca uma
      reserialização do front matter, nunca o front matter enviado pelo
      cliente.
- [ ] Se o documento mudou no GitHub desde que o usuário começou a
      editar (`base_sha` divergente), a submissão é rejeitada com `409`,
      sem criar branch, commit ou PR.
- [ ] Usuário não autorizado recebe `403` e não consegue submeter nada.
- [ ] `owner`, `repo` e a branch base (`main`) continuam fixos no
      backend — nenhum parâmetro de requisição os sobrescreve.
- [ ] Nenhuma permissão além de `Contents: Read and write` e
      `Pull requests: Read and write` é usada.
- [ ] Testes automatizados cobrem sucesso, conflito, autorização, e
      falha em cada chamada ao GitHub (branch/commit/PR), todas
      mockadas.
- [ ] `ruff check`, `pytest`, `eslint`, `vue-tsc` e `vitest` passam.
- [ ] `docs/api/openapi.yaml` reflete o novo endpoint.

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

A ser executado e registrado (mesmo formato de
[docs/phase-1.5-manual-validation.md](phase-1.5-manual-validation.md))
quando a implementação estiver concluída — **requer confirmação explícita
antes de testar contra o `central-ajuda` real**, mesmo que o resultado
seja um PR fechado sem merge:

- [ ] Login com usuário autorizado → editar o documento → enviar → PR
      real criado no `central-ajuda`, com corpo, autor e checklist
      corretos.
- [ ] Conflito: alterar o arquivo diretamente no GitHub entre o
      carregamento e o envio → submissão rejeitada com erro de conflito,
      nenhum branch/commit/PR criado.
- [ ] Usuário sem permissão → tentativa de envio rejeitada, sem criar
      nada no `central-ajuda`.
- [ ] Inspeção do Pull Request criado confirma que nenhuma permissão
      além de `Contents` e `Pull requests` foi necessária.
- [ ] Fechar (sem merge) o(s) Pull Request(s) de teste criados durante a
      validação, ou obter confirmação do mantenedor institucional antes
      de fazer merge de qualquer um deles.

## Dependências

- Fase 2.1 e Fase 2.2 concluídas e validadas (parser, serializer, prévia
  local já funcionando).
- **Ação operacional, fora do código**: atualizar a instalação da GitHub
  App em `cte-zl-ifrn/central-ajuda` para incluir `Contents: Read and
  write` e `Pull requests: Read and write` (hoje restrita a
  `Contents: Read-only` e `Metadata: Read-only`, ver
  [ADR-0004](decisions/0004-integracao-github-app.md)). Sem isso, a
  submissão falha com erro de comunicação com o GitHub (permissão
  insuficiente) — a implementação e os testes automatizados (mockados)
  não dependem dessa atualização, só a validação manual contra o GitHub
  real.
- Confirmação explícita de que é aceitável abrir Pull Requests de teste
  no `central-ajuda` durante a validação manual (ver roteiro acima).

## Decisões em aberto (específicas da Fase 3.1)

- Texto exato do campo de resumo/justificativa no frontend (obrigatório
  ou opcional; tamanho mínimo) — a decidir durante a implementação.
- Formato exato do identificador de submissão usado no nome da branch
  (ex.: sufixo numérico incremental vs. hash curto) — qualquer um serve
  desde que seja razoavelmente único; a decidir na implementação sem
  necessidade de ADR.
