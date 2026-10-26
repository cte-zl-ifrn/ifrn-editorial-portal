# ADR-0011: Estratégia de escrita no central-ajuda (branch, commit e Pull Request)

## Status

Aceita

## Contexto

A Fase 3 ([docs/phase-3-plan.md](../phase-3-plan.md)) ativa, pela primeira
vez, a escrita real no `central-ajuda`: as permissões de escrita da
GitHub App já estavam previstas desde [ADR-0004](0004-integracao-github-app.md)
(`Contents: Read and write`, `Pull requests: Read and write`), mas
deliberadamente restritas a somente leitura durante as Fases 1 e 2 (ver
`docs/phase-1-plan.md`). Antes de dividir a Fase 3 em sub-fases, era
preciso decidir *como* o backend cria a branch, grava o(s) arquivo(s) e
abre o Pull Request, e como trata conflito de edição concorrente — sem
essas decisões, não dá para estimar ou dividir o trabalho com confiança.

## Decisão

### Mecanismo de gravação: chamadas sequenciais à Contents API, não a Git Data API

Cada arquivo alterado (o documento Markdown na Fase 3.1; documento e
assets na Fase 3.2) é gravado com uma chamada
`PUT /repos/{owner}/{repo}/contents/{path}` por arquivo, todas apontando
para a mesma branch de submissão — não a API de baixo nível de blobs/trees/
commits (Git Data API). Cada chamada gera seu próprio commit na branch;
um Pull Request pode perfeitamente conter vários commits, e o
`central-ajuda` já permite squash merge. A Contents API já embute controle
de concorrência otimista via o parâmetro `sha`: gravar com um `sha`
desatualizado retorna `409 Conflict` automaticamente, sem lógica adicional
no backend.

Optamos por isso em vez da Git Data API por ser suficiente para o volume
de arquivos desta fase (1 documento na Fase 3.1; documento + poucos
assets na Fase 3.2) e por reduzir a superfície de código a manter — a
Git Data API exigiria orquestrar blobs, uma tree e um commit manualmente
para o mesmo resultado prático.

### Conflito de concorrência: backend sempre revalida antes de gravar

Imediatamente antes de gravar, o backend busca a versão atual do arquivo
no GitHub (não confia em cache) e compara o `sha` retornado com o
`base_sha` enviado pelo cliente (capturado quando o documento foi
carregado para edição). Se divergirem, o backend retorna erro de
conflito (`409`) sem tentar gravar — nunca sobrescreve silenciosamente,
conforme já determinado na seção 13 de `docs/initial-architecture.md`.

### Front matter: sempre a versão recém-lida, nunca a enviada pelo cliente

Como o front matter continua não editável (ver
[ADR-0009](0009-conversao-markdown-tiptap-e-front-matter.md)), o backend
não confia em um `front_matter_raw` enviado pelo cliente para reconstruir
o arquivo — ele usa o `front_matter_raw` obtido na mesma revalidação que
checa o `base_sha`. Isso fecha, de saída, a possibilidade de um cliente
alterar o front matter por fora da API (mesmo que o frontend hoje não
ofereça essa opção na interface).

### Idempotência: best-effort nesta fase, sem armazenamento de deduplicação

O backend gera um identificador de submissão por requisição e o embute no
nome da branch (`portal/{tipo}/{ano}/{id}-{slug}`, seção 8.3 de
`docs/initial-architecture.md`), mas não mantém nenhum registro
persistente de submissões processadas — coerente com a decisão de MVP
sem banco de dados (ADR-0005). Uma requisição repetida (ex.: um duplo
clique, uma resposta perdida por timeout) pode gerar uma branch e um PR
duplicados. Idempotência real exigiria um armazenamento de deduplicação,
o que já está listado em `docs/initial-architecture.md` (seção 18) como
um gatilho legítimo para introduzir um banco de dados no futuro — não é
resolvido nesta fase.

### Escopo de escrita: só o documento de demonstração fixo, ainda sem escolha de caminho

A Fase 3.1 opera sobre o mesmo documento de demonstração já usado nas
Fases 1 e 2 (`settings.sample_document_path`) — não introduz escolha de
caminho pelo usuário, nem criação de novos documentos
(`_docs/{categoria}/{slug}.md`, seção 8.2 do documento de arquitetura).
Isso fica para uma fase futura, quando a listagem/criação de documentos
for implementada.

## Consequências

- A instalação da GitHub App precisa ser atualizada, fora do código, para
  as permissões completas já previstas na ADR-0004
  (`Contents: Read and write`, `Pull requests: Read and write`) antes de
  a Fase 3.1 poder ser exercitada de ponta a ponta contra o GitHub real —
  isso é uma ação operacional, não uma mudança de código.
- Testes automatizados continuam usando mocks (`respx`) para as novas
  chamadas de escrita — nenhum teste cria branch, commit ou PR reais.
- Uma submissão duplicada por retry é um risco aceito nesta fase (ver
  "Idempotência" acima); deve ser revisitado se se mostrar um problema
  prático quando usuários reais começarem a usar o fluxo de escrita.
- O modelo de autorização não muda: a mesma regra de permissão
  (`write`/`maintain`/`admin`) que já protege a leitura passa a proteger
  também a submissão.

## Referências

- [ADR-0004](0004-integracao-github-app.md) — permissões da GitHub App.
- [ADR-0005](0005-backend-lambda-api-gateway.md) — MVP sem banco de dados.
- [ADR-0006](0006-fluxo-branch-e-pull-request.md) — branch e PR obrigatórios, sem push direto na main.
- [ADR-0009](0009-conversao-markdown-tiptap-e-front-matter.md) — front matter preservado como texto bruto.
- [docs/initial-architecture.md](../initial-architecture.md) — seções 8.2, 8.3, 8.4, 12, 13, 18.
- [docs/phase-3-plan.md](../phase-3-plan.md), [docs/phase-3.1-plan.md](../phase-3.1-plan.md), [docs/phase-3.2-plan.md](../phase-3.2-plan.md).
