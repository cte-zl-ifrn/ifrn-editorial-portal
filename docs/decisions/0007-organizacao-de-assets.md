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
- **A referência gravada no corpo Markdown é uma URL absoluta do GitHub**
  (`https://raw.githubusercontent.com/cte-zl-ifrn/central-ajuda/main/{caminho}`),
  não um caminho relativo. Decisão tomada na validação manual da Fase
  3.2.5, após um achado real: um caminho relativo é resolvido de forma
  diferente pelo GitHub (relativo ao arquivo fonte no repositório) e pelo
  site publicado pelo Jekyll (relativo à URL de saída do `permalink` da
  coleção) — as duas profundidades podem divergir (e divergiam, no
  `central-ajuda`), então nenhum caminho relativo único funciona nos dois
  lugares ao mesmo tempo. Uma URL absoluta do GitHub resolve
  identicamente em qualquer lugar (visualização de arquivo, diff de
  Pull Request e site publicado), sem depender da estrutura de
  permalinks do `central-ajuda`.

## Consequências

- Uploads exigem validação de MIME type, assinatura do arquivo, tamanho,
  texto alternativo (para imagens) e normalização de nome, além de proteção
  contra path traversal e sobrescrita não autorizada.
- Arquivos executáveis, scripts e formatos fora da lista configurada devem
  ser rejeitados.
- Assets de uma submissão são preservados no mesmo Pull Request do
  documento que os referencia.
- A URL absoluta gravada aponta sempre para `main` (nunca para a branch
  da submissão em andamento), então fica quebrada durante a revisão do
  Pull Request, até o merge — troca deliberada: o revisor já vê a
  imagem diretamente na aba "Files changed" do próprio Pull Request.
  Depois do merge, a imagem passa a resolver normalmente em qualquer
  lugar, inclusive ao reabrir o documento no portal para uma nova
  edição (o que um caminho relativo não garantia).
- Documentos com imagens inseridas por uma pessoa editando diretamente o
  `central-ajuda` (fora do portal), usando caminho relativo, continuam
  fora deste mecanismo — não são reescritos retroativamente, e podem não
  ser exibidos corretamente se o documento for reaberto para edição no
  portal. Risco aceito, dado que nenhum documento publicado usava imagem
  antes da Fase 3.2.
- O `permalink` da coleção `docs` do `central-ajuda` tinha um bug
  correlato (duplicava o segmento `docs/docs` na URL publicada,
  ver `_config.yml`), corrigido separadamente nesse repositório — não é
  uma decisão do portal, mas motivou parte deste achado.

## Referências

- [docs/initial-architecture.md](../initial-architecture.md) — seção 11.
