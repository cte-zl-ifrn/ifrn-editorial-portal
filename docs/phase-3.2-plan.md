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

## Critérios de aceite / definição de pronto

- [ ] Uma imagem inserida no Tiptap durante a edição é enviada junto com
      o documento e gravada em `assets/images/{categoria}/` no mesmo
      Pull Request.
- [ ] Um asset com tipo, assinatura ou tamanho inválido é rejeitado antes
      de qualquer gravação, com erro claro — nenhum commit parcial.
- [ ] O caminho final do asset é sempre calculado pelo backend; um nome
      de arquivo malicioso (ex.: contendo `../`) nunca resulta em
      gravação fora de `assets/images/` ou `assets/files/`.
- [ ] O Pull Request resultante lista todos os arquivos alterados
      (documento + assets).
- [ ] Testes automatizados cobrem validação de asset (casos válidos e
      inválidos) e a submissão combinada de documento + assets.
- [ ] `ruff check`, `pytest`, `eslint`, `vue-tsc` e `vitest` passam.

## Riscos técnicos e decisões de arquitetura

- Reaproveita a decisão de gravação da [ADR-0011](decisions/0011-escrita-branch-commit-pull-request.md)
  (Contents API, mesma branch) — nenhuma decisão de mecanismo de commit
  nova é necessária.
- **Risco principal**: upload malicioso (arquivo executável disfarçado,
  SVG com script embutido, arquivo maior que o esperado) — mitigado pela
  validação de MIME/assinatura/tamanho/extensão já prevista desde
  `docs/initial-architecture.md` (seção 11) e pelos requisitos de
  segurança gerais do projeto; nenhuma mitigação nova precisa ser
  inventada, só implementada.
- **Risco**: enviar documento e assets em requisições separadas pode
  deixar a branch em um estado intermediário (documento sem a imagem que
  ele referencia, ou vice-versa) se uma das chamadas falhar — a decisão
  entre uma única requisição multipart/JSON com tudo, ou requisições
  sequenciais na mesma branch com um identificador de submissão comum,
  fica para a implementação, mas deve tratar falha parcial de forma
  visível (nunca abrir o PR se um asset obrigatório falhou).

## Roteiro de validação manual (Fase 3.2.5)

A ser executado e registrado (mesmo formato de
[docs/phase-1.5-manual-validation.md](phase-1.5-manual-validation.md))
quando a implementação estiver concluída — mesma ressalva da Fase 3.1.5
sobre confirmação antes de testar contra o `central-ajuda` real:

- [ ] Inserir uma imagem real (arquivo local) no Tiptap, enviar, e
      confirmar que ela aparece no Pull Request em
      `assets/images/{categoria}/`, referenciada corretamente no
      Markdown do documento.
- [ ] Tentar enviar um arquivo de tipo não permitido (ex.: `.exe`) →
      rejeitado antes de qualquer gravação.
- [ ] Tentar um nome de arquivo com `../` → rejeitado ou normalizado,
      nunca gravado fora de `assets/images/`.
- [ ] Fechar (sem merge) o(s) Pull Request(s) de teste, ou obter
      confirmação do mantenedor institucional antes de merge.

## Dependências

- Fase 3.1 concluída e validada (mecanismo de branch/commit/PR já
  funcionando para o documento).

## Decisões em aberto (específicas da Fase 3.2)

- Uma única requisição (documento + assets juntos) vs. requisições
  sequenciais associadas à mesma submissão — a decidir na implementação,
  documentando a escolha e o tratamento de falha parcial.
- Se `POST /api/assets/validate` (validação prévia, antes de montar a
  submissão completa) entra nesta sub-fase ou é adiada — não bloqueia o
  critério de aceite principal (asset inválido rejeitado na submissão),
  é só uma melhoria de UX (feedback mais cedo).
