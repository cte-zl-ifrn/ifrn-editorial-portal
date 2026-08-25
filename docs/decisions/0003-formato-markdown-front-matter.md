# ADR-0003: Formato de armazenamento em Markdown com front matter YAML

## Status

Aceita

## Contexto

O repositório de conteúdo já usa Jekyll, que consome documentos Markdown com
front matter YAML. O portal precisa gravar conteúdo em um formato que o
pipeline de build existente já entenda, sem exigir mudanças no gerador de
site.

## Decisão

O formato de armazenamento do conteúdo editorial será Markdown com front
matter YAML, seguindo os campos descritos em
[docs/initial-architecture.md](../initial-architecture.md#9-modelo-editorial-markdown)
(`title`, `description`, `category`, `audience`, `tags`, `status`, `author`,
`created_at`, `updated_at`, `submission_id`). O portal não deve permitir
edição livre de campos que alterem o comportamento do site (`layout`,
`permalink`, configurações de build, scripts).

## Consequências

- O modelo editorial do Tiptap deve mapear para esses campos de forma
  controlada — o usuário preenche dados, não o front matter bruto.
- O backend é responsável por validar o front matter antes de qualquer
  gravação ou submissão.
- Suporte a outros formatos (RST/Sphinx) fica fora do MVP.

## Referências

- [docs/initial-architecture.md](../initial-architecture.md) — seção 9.
