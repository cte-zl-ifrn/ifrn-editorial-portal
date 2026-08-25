# ADR-0006: Toda alteração via branch própria e Pull Request, sem push direto na main

## Status

Aceita

## Contexto

O repositório `central-ajuda` é a fonte de verdade do conteúdo publicado e
mantém seu próprio processo de revisão, build e publicação. O portal precisa
propor alterações sem comprometer o histórico, a rastreabilidade ou a
governança editorial já existente.

## Decisão

- Cada submissão do portal cria uma branch própria, derivada da versão atual
  de `main`, com o formato sugerido `portal/{tipo}/{ano}/{id}-{slug}`.
- Cada submissão resulta em um Pull Request contra `main`, com título,
  resumo, autoria, data, tipo de alteração, lista de arquivos e checklist de
  validações.
- O portal nunca faz push direto na branch `main` do repositório de
  conteúdo. A branch `main` deve permanecer protegida, exigindo status
  checks antes do merge.

## Consequências

- Revisão humana, build do Jekyll e demais checks do `central-ajuda`
  continuam sendo a porta de entrada para publicação — o portal não substitui
  esse processo, apenas o alimenta.
- O backend deve gerar identificadores de submissão únicos e verificar
  conflitos de versão antes de gravar (ver seção 13 do documento de
  arquitetura).
- Aprovação editorial completa dentro do portal fica fora do MVP; quem
  aprova e faz merge continua sendo definido pelo processo do
  `central-ajuda`.

## Referências

- [docs/initial-architecture.md](../initial-architecture.md) — seções 4, 8.3, 8.4, 14.
