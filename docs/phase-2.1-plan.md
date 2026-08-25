# Plano da Fase 2.1 — Carregamento e renderização

Sub-fase de [docs/phase-2-plan.md](phase-2-plan.md). Desdobramento da
[issue #11](https://github.com/cte-zl-ifrn/ifrn-editorial-portal/issues/11).

## Objetivo

Buscar um documento Markdown real do `central-ajuda` (via GitHub App, com
as mesmas permissões de leitura já instaladas na Fase 1), separar o front
matter do corpo, e renderizar o corpo no editor Tiptap **em modo somente
leitura** — sem ainda permitir edição (isso é Fase 2.2).

## Escopo

### Dentro

- Backend: separar o conteúdo do arquivo em `front_matter` (dicionário
  parseado, somente para exibição), `front_matter_raw` (texto bruto,
  fonte de verdade — ver [ADR-0009](decisions/0009-conversao-markdown-tiptap-e-front-matter.md))
  e `body` (Markdown sem front matter).
- Backend: atualizar `GET /api/documents/sample` (ou introduzir um
  endpoint equivalente) para retornar essa estrutura, mantendo as mesmas
  regras de autenticação/autorização já validadas na Fase 1
  (`AuthorizedSessionDep`, caminho fixo, sem aceitar `path` arbitrário do
  cliente).
- Frontend: parser Markdown → documento Tiptap para o subconjunto de nós
  já coberto pelo documento de demonstração (parágrafos, títulos, listas,
  negrito, itálico, links, imagens — ver "Escopo de nós" abaixo).
- Frontend: renderizar o `body` convertido no Tiptap com `editable: false`.
- Frontend: exibir os campos do `front_matter` parseado em um painel de
  metadados somente leitura (título, categoria, status etc.), sem
  editá-los.
- Testes automatizados: parser Markdown → Tiptap (Vitest, fixtures
  isoladas) e separação front matter/corpo (pytest).
- Atualizar `docs/api/openapi.yaml` com o novo formato de resposta.

### Fora

- Habilitar edição no Tiptap (Fase 2.2).
- Serializar de volta para Markdown (Fase 2.2).
- Editar campos do front matter.
- Suportar tabelas, blocos de aviso, blocos de código ou passos numerados
  no parser — apenas se o documento de demonstração escolhido já os
  contiver; caso contrário, ficam para quando um documento real os exigir.
- Qualquer escrita no `central-ajuda`.
- Listagem de múltiplos documentos.

## Escopo de nós (parser Markdown → Tiptap)

O parser da Fase 2.1 cobre, no mínimo: parágrafos, títulos (`#`–`######`),
listas com marcadores e numeradas (incluindo listas aninhadas), negrito,
itálico, links e imagens (com texto alternativo). `code` (inline) e
`horizontalRule` foram incluídos incidentalmente por virem de fábrica com
o `@tiptap/starter-kit`, sem custo adicional de implementação.

**Documento de demonstração trocado**: `_docs/ambiente-virtual/acesso-moodle.md`
(usado desde a Fase 1) não continha nenhuma lista com marcadores — apenas
uma lista numerada. Foi substituído por
`_docs/proitec/como-fazer-cursos.md`, que exercita títulos em três
níveis, listas com marcadores e numeradas (inclusive aninhadas), negrito e
links. Nenhum documento atualmente publicado no `central-ajuda` contém
imagem ou itálico — esses dois nós são cobertos apenas por fixtures
isoladas em `frontend/tests/markdownToTiptap.spec.ts`, não pelo documento
de demonstração ao vivo. Isso é uma limitação de conteúdo real disponível,
não do parser.

Nós fora deste conjunto mínimo (tabelas, blocos de aviso reais, blocos de
código, HTML embutido) não são interpretados: um bloco/token desconhecido
é normalizado como texto visível (a partir do Markdown-fonte bruto ou do
conteúdo do próprio token), nunca descartado silenciosamente — ver
`frontend/src/lib/markdownToTiptap.ts`. Em particular, o documento de
demonstração real contém dois blocos `<blockquote class="...">` (um
padrão de "dica"/"aviso" do site) e uma lista de tarefas (`- [x]`); ambos
aparecem como texto literal simples, comprovado por
`frontend/tests/markdownToTiptap.realDocument.spec.ts`, que roda o parser
contra o corpo real do documento.

## Entregáveis

1. Backend: `services/document_service.py` estendido (ou novo serviço) para
   separação front matter/corpo; testes cobrindo documento com/sem front
   matter, front matter malformado.
2. Frontend: módulo `markdownToTiptap` (ou equivalente) com testes de
   unidade por tipo de nó.
3. Frontend: `HomeView.vue` (ou uma view dedicada) passa a renderizar o
   Tiptap em vez do `<pre>` de texto bruto usado na Fase 1.
4. `docs/api/openapi.yaml` atualizado.
5. `docs/glossary.md` atualizado com termos novos (ex.: front matter
   bruto, nó Tiptap).

**Entregue** (nomes de arquivo reais): `backend/src/markdown/front_matter.py`
(+ `backend/src/errors.py:InvalidFrontMatterError`,
`backend/tests/test_front_matter.py`); `backend/src/services/document_service.py`
e `backend/src/models/responses.py` atualizados;
`frontend/src/lib/markdownToTiptap.ts` (+
`frontend/tests/markdownToTiptap.spec.ts` e
`markdownToTiptap.realDocument.spec.ts`);
`frontend/src/components/{FrontMatterPanel,DocumentViewer}.vue`;
`frontend/src/views/HomeView.vue` atualizado.

## Critérios de aceite / definição de pronto

- [x] `GET /api/documents/sample` retorna `front_matter`,
      `front_matter_raw`, `body`, `path`, `name`, `sha` — sem quebrar as
      regras de autorização já existentes (RF-13 a RF-16).
- [x] Um usuário não autorizado continua recebendo HTTP 403, sem receber
      nenhum dos campos do documento.
- [x] O corpo do documento de demonstração é renderizado no Tiptap em modo
      somente leitura (`DocumentViewer.vue`, `editable: false`), visualmente
      equivalente ao Markdown original (título, parágrafos, listas, links).
      Imagens não puderam ser confirmadas visualmente contra o documento
      real (nenhum documento do `central-ajuda` contém imagem hoje — ver
      "Escopo de nós" acima); cobertas por fixtures isoladas.
- [x] O painel de metadados (`FrontMatterPanel.vue`) exibe os campos do
      front matter parseado.
- [x] Testes automatizados cobrem, no mínimo: cada tipo de nó do escopo
      mínimo (`frontend/tests/markdownToTiptap.spec.ts`, 15 casos), o
      corpo real do documento de demonstração
      (`markdownToTiptap.realDocument.spec.ts`), arquivo sem front matter,
      front matter malformado (`backend/tests/test_front_matter.py`,
      `test_documents.py`), e o endpoint com usuário autorizado/não
      autorizado.
- [x] `ruff check`, `pytest` (31 testes), `eslint`, `vue-tsc` e `vitest`
      (38 testes) passam; `npm run build` gera bundle de produção sem erro.
- [x] `docs/api/openapi.yaml` reflete o novo contrato.
- [x] Nenhuma chamada de escrita à API do GitHub foi introduzida.

## Riscos técnicos e decisões de arquitetura

- Ver riscos compartilhados em
  [docs/phase-2-plan.md](phase-2-plan.md#riscos-compartilhados-entre-21-e-22)
  e a decisão de conversão/preservação de front matter em
  [ADR-0009](decisions/0009-conversao-markdown-tiptap-e-front-matter.md).
- Risco específico desta sub-fase: escolher uma biblioteca de tokenização
  Markdown (ex.: `markdown-it`) introduz uma dependência de frontend cujo
  conjunto de sintaxe suportado pode ser mais amplo que o whitelist do
  projeto — o mapeamento token → nó Tiptap deve rejeitar ou sinalizar
  explicitamente qualquer token fora do escopo mínimo definido acima, em
  vez de simplesmente ignorá-lo.
- Risco específico: parsing de front matter malformado (YAML inválido) no
  backend deve resultar em erro tratado (mesmo padrão dos demais erros de
  domínio da Fase 1 — `PortalError` com código estável), não em exceção
  não tratada.

## Roteiro de validação manual (Fase 2.1.5)

A ser executado e registrado (mesmo formato de
[docs/phase-1.5-manual-validation.md](phase-1.5-manual-validation.md))
quando a implementação estiver concluída:

- [ ] Login com usuário autorizado → documento carregado e renderizado no
      Tiptap, comparado visualmente com o Markdown original (mesmos
      títulos, parágrafos, listas, links, imagens).
- [ ] Painel de metadados exibe corretamente os campos do front matter do
      documento real.
- [ ] Login com usuário sem permissão → acesso negado, sem nenhum
      vazamento de conteúdo do documento (nem front matter, nem corpo).
- [ ] Tentativa de editar o conteúdo no Tiptap confirma que o editor está
      em modo somente leitura (nenhuma alteração é possível).
- [ ] Inspeção da resposta de rede confirma que `front_matter_raw` bate
      exatamente com o início do arquivo original no GitHub.

## Dependências

- Fase 1 e Fase 1.5 concluídas (login, sessão, autorização, leitura via
  GitHub App já funcionando).
- Nenhuma dependência de infraestrutura AWS real.

## Decisões tomadas durante a implementação

- Documento de demonstração trocado para `_docs/proitec/como-fazer-cursos.md`
  — ver "Escopo de nós" acima.
- Biblioteca de tokenização Markdown confirmada: `markdown-it`, sem
  plugins (o escopo mínimo de nós não exige nenhum). Configurada com
  `html: false` deliberadamente, para que HTML embutido no Markdown nunca
  seja interpretado como marcação (permanece texto literal) — reforça a
  seção 10.3 do documento de arquitetura sem exigir lógica adicional de
  sanitização nesta fase.
- Imagem misturada a texto corrido no mesmo parágrafo (em vez de ocupar o
  parágrafo inteiro) não é hoisted para um nó de bloco — vira um
  marcador de texto `[imagem: alt]`. Nenhum documento real do
  `central-ajuda` faz isso hoje; documentado como limitação conhecida no
  código-fonte do parser.
