# Fase 2.2.5 — Validação manual

Conclusão operacional da validação manual da Fase 2.2
([docs/phase-2.2-plan.md](phase-2.2-plan.md)): edição do corpo no Tiptap
e serialização de volta para Markdown, testado localmente contra o
backend e o frontend reais.

Data: 2026-08-25

## Resultados

- [x] Editar o documento — mudar um parágrafo.
- [x] Editar o documento — adicionar item de lista.
- [ ] Editar o documento — alterar um link. **Não testado nesta rodada.**
- [x] Prévia mostrando corretamente a sintaxe Markdown de um link.
- [x] Round-trip sem edição: carregar e gerar a prévia sem alterar nada →
      bate com o original (fora das normalizações cosméticas já
      documentadas em `tiptapToMarkdown.ts`, como itálico sempre virar
      `*...*`).
- [x] Aba de rede confirma que nenhuma requisição de escrita (POST/PUT/PATCH)
      ocorre durante a edição.
- [x] Front matter da prévia idêntico ao `front_matter_raw` retornado pela
      API.

## Observações

- A edição de link em si (criar/alterar via o botão "Link" da toolbar, que
  usa `window.prompt`) não foi exercitada nesta rodada — apenas a
  renderização de um link já existente na prévia foi confirmada. Fica
  como pendência para uma validação futura, não bloqueia a conclusão da
  Fase 2.2 nem o início da Fase 3: o comportamento de serialização de
  links já está coberto por testes automatizados
  (`frontend/tests/tiptapToMarkdown.spec.ts` e `roundtrip.spec.ts`), só
  falta a confirmação manual da interação via toolbar.
- Mesma ressalva já registrada na Fase 2.1.5 continua valendo: a
  validação usou o documento de demonstração então configurado localmente
  (não necessariamente `_docs/proitec/como-fazer-cursos.md`, o padrão
  atual) — lista com marcadores foi exercitada nesta rodada (item
  adicionado com sucesso), mas itálico e imagem seguem cobertos apenas
  pelos testes automatizados.

## Efeito nos critérios de aceite da Fase 2.2

A maior parte do roteiro de validação manual definido em
[docs/phase-2.2-plan.md](phase-2.2-plan.md#roteiro-de-validação-manual-fase-225)
foi confirmada: edição de parágrafo e lista, prévia correta, round-trip
estável, nenhuma escrita de rede, e front matter preservado
exatamente. A Fase 2.2 é considerada concluída — a interação de edição de
link via toolbar é a única lacuna, e é de baixo risco dado que a lógica de
serialização de links já tem cobertura automatizada.
