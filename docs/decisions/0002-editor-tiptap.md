# ADR-0002: Editor de conteúdo baseado em Tiptap

## Status

Aceita

## Contexto

Os autores de conteúdo da Central de Ajuda não devem precisar conhecer a
sintaxe Markdown nem a interface do GitHub para propor alterações. É preciso
um editor visual e estruturado que produza um documento previsível, capaz de
ser convertido para Markdown de forma determinística.

## Decisão

O editor de conteúdo do portal será o Tiptap, com um modelo de nós
controlado (parágrafos, títulos, listas, negrito, itálico, links, imagens,
tabelas, blocos de aviso, blocos de código, passos numerados, separadores e
texto alternativo de imagens). O usuário edita esse modelo, não Markdown ou
HTML livre.

## Consequências

- É necessário implementar um parser Markdown → documento Tiptap e um
  serializer documento Tiptap → Markdown, ambos determinísticos e testados
  com testes de round-trip.
- Conteúdo HTML ou Markdown fora do modelo permitido deve ser rejeitado ou
  sanitizado (scripts, handlers `on*`, iframes não autorizados, SVG com
  script, URLs com esquemas perigosos).
- A fidelidade da conversão é um risco relevante do projeto (ver seção de
  riscos em [docs/project-context.md](../project-context.md)).

## Referências

- [docs/initial-architecture.md](../initial-architecture.md) — seções 6.1, 9, 10.
