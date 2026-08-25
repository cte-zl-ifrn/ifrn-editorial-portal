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

## Critérios de aceite / definição de pronto

- [ ] O corpo do documento é editável no Tiptap (negrito, itálico,
      títulos, listas, links, imagens).
- [ ] Serializar o documento editado produz Markdown válido para todos os
      tipos de nó do escopo.
- [ ] Round-trip sem edição (carregar → serializar sem alterar nada)
      reproduz o `body` original ou uma normalização documentada e estável
      (sem perda de conteúdo ou formatação).
- [ ] O documento final para prévia é `front_matter_raw` (inalterado) +
      `body` serializado — nunca uma reserialização do front matter.
- [ ] Nenhuma requisição de escrita é enviada ao backend ou ao GitHub em
      nenhum momento do fluxo de edição.
- [ ] Testes automatizados cobrem o serializer por tipo de nó e pelo menos
      3 fixtures de round-trip com documentos reais.
- [ ] `ruff check`, `pytest`, `eslint`, `vue-tsc` e `vitest` passam.

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

## Decisões em aberto (específicas da Fase 2.2)

- Nível de normalização cosmética aceitável no round-trip (ex.: estilo de
  marcador de lista, aspas) — a decidir durante a implementação e
  documentar no próprio serializer (comentário + teste), não como ADR
  separada a menos que se mostre uma decisão controversa.
- Se a prévia do Markdown deve ficar visível permanentemente na interface
  desta fase ou ser um recurso temporário de depuração para a validação
  manual — não afeta o backend nem o contrato de API, pode ser decidido
  livremente durante a implementação do frontend.
