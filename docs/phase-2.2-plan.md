# Plano da Fase 2.2 — Edição e serialização

Sub-fase de [docs/phase-2-plan.md](phase-2-plan.md), depende da conclusão
de [docs/phase-2.1-plan.md](phase-2.1-plan.md). Desdobramento da
[issue #11](https://github.com/cte-zl-ifrn/ifrn-editorial-portal/issues/11).

## Objetivo

Permitir a edição do corpo do documento no Tiptap (habilitado na Fase 2.1
apenas em modo somente leitura) e serializar o resultado de volta para
Markdown, recombinando com o front matter original preservado
(`front_matter_raw`, ver [ADR-0009](decisions/0009-conversao-markdown-tiptap-e-front-matter.md)),
**sem persistir ou enviar nada ao `central-ajuda`** — isso é Fase 3.

## Escopo

### Dentro

- Frontend: habilitar `editable: true` no Tiptap para o subconjunto de nós
  já suportado pelo parser da Fase 2.1.
- Frontend: serializer Tiptap → Markdown (documento JSON → texto Markdown),
  escrito à mão conforme decidido em ADR-0009, cobrindo o mesmo escopo de
  nós da Fase 2.1.
- Frontend: reconstrução do documento completo
  (`front_matter_raw + "\n" + body_serializado`) para fins de exibição
  local (prévia), sem envio ao backend para gravação.
- Testes de **round-trip**: para cada fixture de Markdown de entrada,
  `markdownToTiptap(markdownToTiptap(md).then(tiptapToMarkdown)) === md`
  (ou equivalente semântico, quando a normalização for esperada e
  documentada — ex.: espaçamento entre blocos).
- Uma tela/seção de **prévia** mostrando o Markdown resultante (para
  inspeção manual durante a validação), deixando claro visualmente que
  nada foi salvo.

### Fora

- Qualquer chamada ao backend para gravar o documento editado.
- Criação de branch, commit ou Pull Request (Fase 3).
- Edição dos campos do front matter — permanece somente leitura,
  preservado verbatim.
- Detecção de conflito de edição concorrente (`base_sha`) — só é relevante
  quando houver gravação real (Fase 3).
- Suporte a nós fora do escopo já definido na Fase 2.1.

## Entregáveis

1. Frontend: módulo `tiptapToMarkdown` (serializer), com testes de unidade
   por tipo de nó e testes de round-trip com fixtures reais.
2. Frontend: Tiptap editável na view de edição, com toolbar mínima para os
   nós suportados (negrito, itálico, títulos, listas, links, imagem).
3. Frontend: painel/seção de prévia do Markdown resultante.
4. Suite de fixtures de round-trip (arquivo(s) de teste com exemplos reais
   de Markdown do `central-ajuda`, cobrindo o escopo de nós da Fase 2.1).

**Entregue** (nomes de arquivo reais): `frontend/src/lib/tiptapToMarkdown.ts`
(serializer + `UnsupportedNodeError`); `frontend/src/lib/tiptapExtensions.ts`
(configuração do StarterKit restrita ao whitelist, compartilhada entre
leitura e edição); `frontend/src/components/DocumentViewer.vue` estendido
com prop `editable`, toolbar e emissão de `update:content`;
`frontend/src/views/HomeView.vue` com a seção de prévia;
`frontend/tests/{tiptapToMarkdown,roundtrip}.spec.ts` e
`frontend/tests/fixtures/realDocuments.ts` (compartilhada com os testes
da Fase 2.1).

## Critérios de aceite / definição de pronto

- [x] O corpo do documento é editável no Tiptap (negrito, itálico,
      títulos H1–H3, listas, links, imagens), com toolbar mínima
      (`DocumentViewer.vue`).
- [x] Serializar o documento editado produz Markdown válido para todos os
      tipos de nó do escopo (`tiptapToMarkdown.ts`, 15 testes por tipo de nó).
- [x] Round-trip sem edição (carregar → serializar sem alterar nada)
      reproduz uma árvore Tiptap semanticamente idêntica à original ao
      reanalisar o Markdown serializado — normalização documentada e
      estável (itálico sempre `*...*`; softbreak e hardbreak colapsam no
      mesmo nó `hardBreak`, serializado como `\` + nova linha), sem perda
      de conteúdo ou estrutura.
- [x] O documento final para prévia (`HomeView.vue`) é `front_matter_raw`
      (inalterado) + `body` serializado — nunca uma reserialização do
      front matter.
- [x] Nenhuma requisição de escrita é enviada ao backend ou ao GitHub em
      nenhum momento do fluxo de edição (a prévia é só client-side).
- [x] Testes automatizados cobrem o serializer por tipo de nó (15) e
      round-trip contra os 3 documentos reais do `central-ajuda` já
      usados na Fase 2.1, mais um documento sintético cobrindo todo o
      escopo mínimo (`tests/roundtrip.spec.ts`, 4 testes). Componente:
      edição habilitada, toolbar visível, emissão do documento atual
      (`update:content`) e aplicação de negrito via toolbar
      (`DocumentViewer.spec.ts`).
- [x] `ruff check`, `pytest` (31), `eslint`, `vue-tsc` e `vitest` (60)
      passam; `npm run build` gera bundle de produção sem erro.

## Riscos técnicos e decisões de arquitetura

- Ver [ADR-0009](decisions/0009-conversao-markdown-tiptap-e-front-matter.md)
  (serializer próprio, front matter preservado como texto bruto) e os
  riscos compartilhados em
  [docs/phase-2-plan.md](phase-2-plan.md#riscos-compartilhados-entre-21-e-22).
- Risco específico: normalização cosmética inevitável (ex.: `*itálico*`
  vs. `_itálico_`, quebras de linha entre parágrafos) pode fazer um
  round-trip "sem edição" não ser byte-a-byte idêntico ao original. Isso é
  aceitável se documentado e estável (mesma normalização sempre), mas deve
  ser tratado como um risco explícito de diff cosmético em Pull Requests
  futuros (Fase 3) — não deve ser ignorado nem "resolvido" escondendo a
  normalização.
- Risco específico: editar um documento com nós fora do escopo mínimo
  (ex.: uma tabela) e serializar de volta pode perder ou corromper esse
  conteúdo se o serializer não tratar esse caso explicitamente — o
  serializer deve detectar nós desconhecidos e falhar de forma visível
  (erro tratado), nunca descartar conteúdo silenciosamente.

## Roteiro de validação manual (Fase 2.2.5)

A ser executado e registrado (mesmo formato de
[docs/phase-1.5-manual-validation.md](phase-1.5-manual-validation.md))
quando a implementação estiver concluída:

- [ ] Login com usuário autorizado → documento carregado, editado (ex.:
      alterar um parágrafo, adicionar um item de lista, alterar um link) →
      prévia do Markdown resultante exibida corretamente.
- [ ] Round-trip sem edição: carregar o documento e gerar a prévia sem
      alterar nada → comparar manualmente com o arquivo original no
      `central-ajuda` (diferenças, se houver, devem ser só as
      normalizações documentadas).
- [ ] Confirmar, inspecionando a aba de rede do navegador, que nenhuma
      requisição de escrita (POST/PUT/PATCH para o GitHub ou para o
      backend persistir o documento) ocorre durante a edição.
- [ ] Front matter da prévia idêntico, caractere a caractere, ao
      `front_matter_raw` retornado na Fase 2.1.
- [ ] Login com usuário sem permissão → sem acesso ao editor (mesmo
      comportamento validado na Fase 2.1.5).

## Dependências

- Fase 2.1 concluída e validada (parser Markdown → Tiptap, separação de
  front matter, documento(s) de referência definidos).

## Decisões tomadas durante a implementação

- Normalização cosmética do round-trip, documentada no cabeçalho de
  `tiptapToMarkdown.ts`: itálico sempre serializa como `*...*` (nunca
  `_..._`, mesmo que o original usasse underscore); quebras de linha
  suaves e forçadas colapsam no mesmo nó `hardBreak` (já era assim desde
  a Fase 2.1) e serializam de volta como `\` + nova linha. Nenhuma perde
  conteúdo — apenas normalizam a sintaxe de superfície de forma estável.
  Verificado com testes de round-trip semântico (reanalisar o Markdown
  serializado reproduz a mesma árvore Tiptap), não comparação byte-a-byte.
- Colchetes (`[`/`]`) não são escapados no texto simples, mesmo sendo
  tecnicamente "significativos" em Markdown — escapá-los sempre
  distorceria visualmente conteúdo comum como checklists em texto puro
  (`[x] Tarefa`), presente em documentos reais do `central-ajuda`, e um
  `[texto]` isolado sem `(` logo depois não é interpretado como link pelo
  CommonMark de qualquer forma.
- A prévia (`front_matter_raw + body serializado`) ficou permanentemente
  visível em `HomeView.vue`, como uma seção própria — mais simples do que
  um recurso de depuração escondido, e útil diretamente para a validação
  manual da Fase 2.2.5.
- A superfície de edição do Tiptap foi restringida (`tiptapExtensions.ts`)
  para desabilitar blockquote, codeBlock, strike e underline do
  StarterKit — nós fora do whitelist que o serializer não sabe
  serializar. Isso evita que o usuário crie, sem querer, um documento que
  o `UnsupportedNodeError` do serializer rejeitaria; o erro tratado
  continua como defesa em profundidade, não como mecanismo primário.
