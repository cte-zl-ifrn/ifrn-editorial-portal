# Plano da Fase 3.2 — Assets (imagens/arquivos)

Sub-fase de [docs/phase-3-plan.md](phase-3-plan.md), depende da conclusão
de [docs/phase-3.1-plan.md](phase-3.1-plan.md). Desdobramento da
[issue #12](https://github.com/cte-zl-ifrn/ifrn-editorial-portal/issues/12).

## Objetivo

Adicionar suporte a upload de imagens e arquivos referenciados pelo
documento editado, gravando-os no `central-ajuda` como parte do mesmo
branch e Pull Request criados na Fase 3.1 — sem introduzir um segundo
fluxo de submissão.

## Escopo

### Dentro

- Backend: aceitar, na mesma requisição de submissão (ou em requisições
  adicionais associadas à mesma branch/submissão — a decidir na
  implementação), um ou mais assets a gravar em `assets/images/` ou
  `assets/files/` (ADR-0007), cada um com conteúdo (base64), nome e,
  para imagens, texto alternativo.
- Backend: validação de cada asset antes de gravar — MIME type,
  assinatura do arquivo (magic bytes), extensão permitida, tamanho
  máximo, normalização de nome, e proteção contra path traversal (ver
  seção 11 do documento de arquitetura e requisitos RNF já existentes).
- Backend: gravação de cada asset via Contents API na mesma branch da
  Fase 3.1 (chamadas sequenciais adicionais, mesmo mecanismo da
  ADR-0011).
- Backend: cálculo do caminho final do asset a partir da localização do
  documento e da categoria configurada — nunca aceito literalmente do
  cliente.
- Frontend: upload de imagem pelo botão "Imagem" da toolbar do Tiptap
  (já existente desde a Fase 2.2, hoje só aceita uma URL já publicada) —
  passa a aceitar também um arquivo local, exibindo uma prévia antes do
  envio.
- Atualizar `docs/api/openapi.yaml` com o novo formato de submissão
  (incluindo assets) e, se aplicável, um endpoint de validação prévia de
  asset (`POST /api/assets/validate`, já sugerido na seção 12 do
  documento de arquitetura).

### Fora

- Upload de arquivos para download (`assets/files/`) diretamente pela
  toolbar do Tiptap — o escopo inicial de inserção via editor é só
  imagem; um arquivo para download vinculado ao texto (ex.: um link
  "baixe o manual") pode ficar para depois, se o Tiptap não tiver um nó
  nativo para isso.
- Reescrita de imagens já existentes no corpo do documento (troca de uma
  imagem por outra) além do que a edição normal do Tiptap já permite
  (remover o nó e inserir um novo).
- Qualquer alteração no mecanismo de branch/PR em si — reaproveita
  integralmente o que a Fase 3.1 já implementou.
- Compressão, redimensionamento ou qualquer processamento de imagem além
  da validação — o arquivo é gravado como enviado.

## Entregáveis

1. Backend: serviço de validação de asset (MIME, assinatura, tamanho,
   extensão, normalização de nome) reutilizável por documento e por
   asset avulso.
2. Backend: extensão do `submission_service.py` da Fase 3.1 para gravar
   assets na mesma branch.
3. Frontend: upload de arquivo local a partir do botão "Imagem" da
   toolbar, com prévia antes do envio.
4. Testes: assets válidos e inválidos (tipo errado, tamanho excedido,
   assinatura incompatível com a extensão, tentativa de path traversal
   no nome), e submissão combinada (documento + assets) na mesma branch.

**Entregue** (nomes de arquivo reais): `backend/src/assets/validation.py`
(+ `backend/src/errors.py:InvalidAssetError`,
`backend/tests/test_asset_validation.py`, 18 testes);
`backend/src/services/submission_service.py` estendido para validar e
gravar assets antes de abrir o PR;
`backend/src/models/requests.py:AssetInput`;
`backend/src/models/responses.py:SubmissionResponse.asset_paths`;
`backend/src/github/client.py:update_file_content` agora aceita `sha`
opcional (arquivo novo vs. atualização) e conteúdo binário.
`frontend/src/lib/pendingAssets.ts` (resolução de upload local → caminho
final + extração do asset, com testes em
`frontend/tests/pendingAssets.spec.ts`); `DocumentViewer.vue` (botão
"Imagem" agora abre um seletor de arquivo local, com prévia via `data:`
URL); `HomeView.vue` (prévia e envio usam o mesmo documento resolvido,
para que os nomes de arquivo batam nos dois lugares).

## Critérios de aceite / definição de pronto

- [x] Uma imagem inserida no Tiptap durante a edição é enviada junto com
      o documento e gravada em `assets/images/{categoria}/` no mesmo
      Pull Request (`submission_service.py`, testado com mocks em
      `test_submission_with_image_asset_writes_it_alongside_the_document`).
- [x] Um asset com tipo, assinatura ou tamanho inválido é rejeitado antes
      de qualquer gravação, com erro claro (`InvalidAssetError`, 422) —
      testado explicitamente checando que nenhuma rota do GitHub é
      chamada quando isso acontece.
- [x] O caminho final do asset é sempre calculado pelo backend a partir
      do documento fixo; um nome de arquivo malicioso (contendo `../`,
      `/`, maiúsculas ou sem extensão) é rejeitado pelo padrão de nome
      validado em `src/assets/validation.py`.
- [x] O Pull Request resultante lista todos os arquivos alterados
      (documento + assets) — `_build_pull_request_body` agora recebe a
      lista completa de arquivos.
- [x] Testes automatizados cobrem validação de asset (18 casos válidos e
      inválidos) e a submissão combinada de documento + assets (62
      testes no total no backend, 73 no frontend).
- [x] `ruff check`, `pytest`, `eslint`, `vue-tsc` e `vitest` passam;
      `npm run build` gera bundle de produção sem erro.

## Riscos técnicos e decisões de arquitetura

- Reaproveita a decisão de gravação da [ADR-0011](decisions/0011-escrita-branch-commit-pull-request.md)
  (Contents API, mesma branch) — nenhuma decisão de mecanismo de commit
  nova foi necessária; `update_file_content` passou a aceitar `sha`
  opcional (omitido para arquivo novo, obrigatório para atualização).
- **Risco principal**: upload malicioso — mitigado por validação de
  assinatura/magic bytes (não só a extensão declarada), tamanho máximo
  configurável (`MAX_IMAGE_SIZE_BYTES`/`MAX_FILE_SIZE_BYTES`) e uma lista
  de extensões permitida. **SVG foi deliberadamente excluído** do
  conjunto de extensões de imagem aceitas nesta fase: a seção 11.2 do
  documento de arquitetura exige "rejeitar conteúdo SVG perigoso", o que
  demandaria sanitização de XML/script — desnecessário para o MVP, já
  que nenhum documento real usa SVG hoje. Reavaliar se isso se tornar
  necessário.
- Assets são validados **antes** de qualquer chamada ao GitHub (branch,
  commit do documento ou dos assets) — um asset inválido nunca deixa uma
  branch ou commit pela metade; testado explicitamente.

## Roteiro de validação manual (Fase 3.2.5)

A ser executado e registrado (mesmo formato de
[docs/phase-1.5-manual-validation.md](phase-1.5-manual-validation.md))
quando a implementação estiver concluída — mesma ressalva da Fase 3.1.5
sobre confirmação antes de testar contra o `central-ajuda` real:

- [x] Inserir uma imagem real (arquivo local) no Tiptap, enviar, e
      confirmar que ela aparece no Pull Request em
      `assets/images/{categoria}/`, referenciada corretamente no
      Markdown do documento. Confirmado em
      [cte-zl-ifrn/central-ajuda#2](https://github.com/cte-zl-ifrn/central-ajuda/pull/2):
      duas imagens inseridas na mesma edição, cada uma gravada com nome
      próprio (`assets/images/proitec/como-fazer-cursos-c44065ad.png` e
      `...-c15bda0f.png`) e referenciada corretamente no Markdown
      (`![alt](../../assets/images/proitec/...)`).
- [x] Tentar selecionar um arquivo de tipo não permitido (ex.: `.exe`) →
      rejeitado **imediatamente na seleção**, no frontend, sem sequer
      criar uma prévia. Reescrito após um achado da validação manual: a
      validação original só existia no backend (`assinatura do arquivo`,
      `422`); o `accept` do `<input type="file">` é só uma dica de UI, e
      o sistema operacional permitiu escolher um `.exe` mesmo assim — o
      frontend o inseria como imagem quebrada (não renderiza, mas também
      não avisava nada) em vez de rejeitar. Corrigido em `setImage`
      (`DocumentViewer.vue`), que agora confere `file.type` contra
      `ACCEPTED_IMAGE_MIME_TYPES` antes de prosseguir. Reteste confirmado
      pelo usuário após a correção.
- [x] Tentar um nome de arquivo com `../` → **não aplicável via UI**,
      por desenho: o frontend gera o próprio nome do arquivo
      (`{slug}-{id}.{ext}`, ver `pendingAssets.ts`), não existe campo
      onde um nome malicioso possa ser digitado. A proteção equivalente
      já é validada automaticamente em
      `backend/tests/test_asset_validation.py` (18 casos, incluindo
      `../../etc/passwd.png`, `/etc/passwd.png`, `..\windows\...` etc.) —
      coberto por teste automatizado, não por passo manual.
- [x] Fechar (sem merge) o(s) Pull Request(s) de teste, ou obter
      confirmação do mantenedor institucional antes de merge — todos os
      Pull Requests de teste
      ([#1](https://github.com/cte-zl-ifrn/central-ajuda/pull/1),
      [#2](https://github.com/cte-zl-ifrn/central-ajuda/pull/2),
      [#3](https://github.com/cte-zl-ifrn/central-ajuda/pull/3),
      [#5](https://github.com/cte-zl-ifrn/central-ajuda/pull/5)) foram
      mergeados de verdade pelo mantenedor institucional. Detalhes em
      [docs/phase-3.2.5-manual-validation.md](phase-3.2.5-manual-validation.md).

### Achado adicional (fora do roteiro original): imagem não aparece ao reabrir o documento — resolvido

Ao reabrir para edição o documento já submetido em
[central-ajuda#2](https://github.com/cte-zl-ifrn/central-ajuda/pull/2), a
imagem não era exibida. Investigação aprofundada mostrou que a causa não
era só a origem do portal: o caminho relativo gravado
(`../../assets/images/...`) é resolvido pelo GitHub a partir do arquivo
fonte (`_docs/proitec/como-fazer-cursos.md`, 2 níveis), mas pelo site
publicado pelo Jekyll a partir da URL de saída do `permalink` da
coleção (`/central-ajuda/docs/docs/proitec/como-fazer-cursos/`, 4
níveis) — as duas profundidades divergem, então nenhum caminho relativo
funciona nos dois lugares ao mesmo tempo (detalhe completo e achado
correlato do `permalink` duplicado do `central-ajuda` na
[ADR-0007](decisions/0007-organizacao-de-assets.md)).

**Corrigido**: a referência gravada agora é uma URL absoluta do GitHub
(`https://raw.githubusercontent.com/cte-zl-ifrn/central-ajuda/main/assets/images/{categoria}/{arquivo}`),
calculada em `computeAssetUrl` (`frontend/src/lib/pendingAssets.ts`),
que substituiu o cálculo de caminho relativo por profundidade
(`computeAssetPathPrefix`, removido). Resolve o problema original (a
mesma URL funciona ao reabrir o documento no portal) sem depender da
estrutura de permalinks do `central-ajuda` — ver ADR-0007 para o
trade-off aceito (a URL só resolve depois do merge do Pull Request, já
que aponta para `main`).

## Dependências

- Fase 3.1 concluída e validada (mecanismo de branch/commit/PR já
  funcionando para o documento).

## Decisões tomadas durante a implementação

- **Uma única requisição** (documento + assets juntos em
  `POST /api/submissions`), não requisições sequenciais — o backend
  valida todos os assets antes de qualquer chamada ao GitHub, então uma
  falha de validação nunca deixa a branch pela metade. Uma falha de
  *escrita* no GitHub após a branch já existir (ex.: um asset cujo nome
  colide com um arquivo já existente) continua sendo o mesmo risco
  aceito de falha parcial já documentado na ADR-0011 para o documento.
- `POST /api/assets/validate` (validação prévia antes de montar a
  submissão completa) **não foi implementado** nesta fase — não
  bloqueava o critério de aceite principal, e a submissão única já dá
  feedback claro (422 com o motivo) sem precisar de uma chamada extra.
  Pode ser adicionado depois como melhoria de UX.
- Caminho do asset determinado pelo **frontend** no momento da inserção
  (categoria + slug do documento + id aleatório), não pelo backend no
  momento do envio — necessário porque o corpo Markdown precisa
  referenciar o caminho final antes de a submissão existir (ver
  `frontend/src/lib/pendingAssets.ts`). O backend segue sendo quem
  valida e decide o diretório de verdade (ADR-0007) — o nome sugerido
  pelo frontend é só isso, uma sugestão, sempre validada.
- Upload de imagem na toolbar do Tiptap passou a ser **só arquivo
  local** (antes era só URL, na Fase 2.2) — não oferece as duas opções
  para não introduzir um mini-diálogo de escolha; documentado como troca
  deliberada de escopo.
