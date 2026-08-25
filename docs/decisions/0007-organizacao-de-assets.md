# ADR-0007: Organização de assets em assets/images e assets/files

## Status

Aceita

## Contexto

Documentos editoriais frequentemente referenciam imagens e arquivos para
download. É preciso um local previsível e validável para esses assets dentro
do repositório de conteúdo, calculado pelo backend e não escolhido livremente
pelo usuário.

## Decisão

- Imagens enviadas pelo portal são gravadas em `assets/images/{categoria}/`,
  com nome normalizado no formato `{categoria}/{slug}-{id}.{extensão}`.
- Arquivos para download são gravados em `assets/files/{categoria}/`, com o
  mesmo padrão de nomenclatura, limitados a uma lista configurável de
  extensões permitidas (inicialmente `.pdf`, `.docx`, `.xlsx`, `.odt`,
  `.ods`, `.zip`).
- O caminho final é sempre calculado e validado pelo backend a partir da
  localização do documento, nunca informado livremente pelo usuário.

## Consequências

- Uploads exigem validação de MIME type, assinatura do arquivo, tamanho,
  texto alternativo (para imagens) e normalização de nome, além de proteção
  contra path traversal e sobrescrita não autorizada.
- Arquivos executáveis, scripts e formatos fora da lista configurada devem
  ser rejeitados.
- Assets de uma submissão são preservados no mesmo Pull Request do
  documento que os referencia.

## Referências

- [docs/initial-architecture.md](../initial-architecture.md) — seção 11.
