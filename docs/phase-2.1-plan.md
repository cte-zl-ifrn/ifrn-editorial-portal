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

Baseado no documento de demonstração atual
(`_docs/ambiente-virtual/acesso-moodle.md`), o parser da Fase 2.1 precisa
cobrir, no mínimo: parágrafos, títulos (`#`–`######`), listas com
marcadores e numeradas, negrito, itálico, links e imagens (com texto
alternativo). Se, ao implementar, o documento de demonstração não exercitar
algum desses nós, o documento de demonstração deve ser trocado por outro
real do `central-ajuda` que os exercite (não inventar Markdown sintético
apenas para testar) — documentar a escolha, como já feito na Fase 1 para
`_docs/ambiente-virtual/acesso-moodle.md`.

Nós fora deste conjunto mínimo (tabelas, blocos de aviso, blocos de
código, separadores, passos numerados) ficam explicitamente fora da Fase
2.1; se aparecerem no corpo do documento de demonstração, devem ser
preservados como texto bruto/nó genérico visível (não removidos
silenciosamente) até serem suportados.

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

## Critérios de aceite / definição de pronto

- [ ] `GET /api/documents/sample` retorna `front_matter`,
      `front_matter_raw`, `body`, `path`, `name`, `sha` — sem quebrar as
      regras de autorização já existentes (RF-13 a RF-16).
- [ ] Um usuário não autorizado continua recebendo HTTP 403, sem receber
      nenhum dos campos do documento.
- [ ] O corpo do documento de demonstração é renderizado no Tiptap em modo
      somente leitura, visualmente equivalente ao Markdown original (título,
      parágrafos, listas, links, imagens reconhecíveis).
- [ ] O painel de metadados exibe os campos do front matter parseado.
- [ ] Testes automatizados cobrem, no mínimo: cada tipo de nó do escopo
      mínimo (parser), arquivo sem front matter, front matter malformado
      (backend), e o endpoint com usuário autorizado/não autorizado.
- [ ] `ruff check`, `pytest`, `eslint`, `vue-tsc` e `vitest` passam.
- [ ] `docs/api/openapi.yaml` reflete o novo contrato.
- [ ] Nenhuma chamada de escrita à API do GitHub foi introduzida.

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

## Decisões em aberto (específicas da Fase 2.1)

- Se o documento de demonstração atual não cobrir todos os nós do escopo
  mínimo, qual documento real do `central-ajuda` o substitui (a decidir
  durante a implementação, documentando a escolha como já feito na Fase 1).
- Biblioteca específica de tokenização Markdown a adotar no frontend
  (`markdown-it` é a opção recomendada em ADR-0009, a confirmar com um
  spike curto no início da implementação).
