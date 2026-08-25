# Decisões de arquitetura (ADRs)

Este diretório reúne os *Architecture Decision Records* (ADRs) do
`ifrn-editorial-portal`: registros curtos que documentam uma decisão
arquitetural ou de produto, o contexto que a motivou e suas consequências.

O objetivo é permitir que qualquer pessoa (ou agente) entenda **por que** o
projeto é como é, sem precisar reconstruir a discussão original. Decisões já
tomadas não devem ser reabertas silenciosamente — se uma delas precisar
mudar, registre uma nova ADR que a substitua.

## Formato

Cada ADR é um arquivo Markdown numerado sequencialmente, com a estrutura:

```markdown
# ADR-NNNN: Título da decisão

## Status

Proposta | Aceita | Substituída por ADR-XXXX | Obsoleta

## Contexto

Qual problema ou pergunta motivou a decisão.

## Decisão

O que foi decidido, de forma direta.

## Consequências

O que essa decisão implica, habilita ou restringe.

## Referências

Links para o documento de arquitetura ou outras ADRs relacionadas.
```

## Índice

| ADR | Título | Status |
|---|---|---|
| [0001](0001-separacao-portal-e-repositorio-de-conteudo.md) | Separação entre o portal e o repositório de conteúdo | Aceita |
| [0002](0002-editor-tiptap.md) | Editor de conteúdo baseado em Tiptap | Aceita |
| [0003](0003-formato-markdown-front-matter.md) | Formato de armazenamento em Markdown com front matter YAML | Aceita |
| [0004](0004-integracao-github-app.md) | Integração com o GitHub via GitHub App | Aceita |
| [0005](0005-backend-lambda-api-gateway.md) | Backend inicial em AWS Lambda + API Gateway HTTP API | Aceita |
| [0006](0006-fluxo-branch-e-pull-request.md) | Toda alteração via branch própria e Pull Request, sem push direto na main | Aceita |
| [0007](0007-organizacao-de-assets.md) | Organização de assets em `assets/images` e `assets/files` | Aceita |

## Como propor uma nova ADR

1. Copie o formato acima para um novo arquivo `NNNN-titulo-curto.md`, usando
   o próximo número sequencial.
2. Descreva o contexto e a decisão de forma objetiva — evite misturar várias
   decisões não relacionadas em uma única ADR.
3. Adicione a linha correspondente ao índice acima.
4. Se a nova ADR substituir uma decisão anterior, atualize o status da ADR
   antiga para "Substituída por ADR-NNNN" em vez de apagá-la.

Para o panorama completo do produto e da arquitetura, veja
[docs/initial-architecture.md](../initial-architecture.md) e
[docs/project-context.md](../project-context.md).

## Como foi estruturado

As 10 decisões iniciais foram agrupadas em 7 ADRs. O agrupamento foi feito para manter juntas decisões que formam uma única unidade arquitetural ou operacional.

| ID   | Decisão                          | ADR     |
| ---- | -------------------------------- | ------- |
| D-01 | Separação portal/conteúdo        | ADR-001 |
| D-02 | Repositório único de conteúdo    | ADR-001 |
| D-03 | Escopo restrito ao central-ajuda | ADR-001 |
| D-04 | Editor Tiptap                    | ADR-002 |
| D-05 | Markdown e front matter          | ADR-003 |
| D-06 | GitHub App                       | ADR-004 |
| D-07 | AWS Lambda e API Gateway         | ADR-005 |
| D-08 | Branch por alteração             | ADR-006 |
| D-09 | Pull Request obrigatório         | ADR-006 |
| D-10 | Assets globais                   | ADR-007 |

## Matriz decisão–risco–validação

| Decisão        | Risco associado                     | Validação futura                |
| -------------- | ----------------------------------- | ------------------------------- |
| Tiptap         | Conversão imperfeita para Markdown  | Testes de round-trip            |
| GitHub App     | Permissões excessivas               | Teste em repositório controlado |
| Lambda         | Complexidade de autenticação e CORS | Spike técnico                   |
| Branch + PR    | Conflitos de edição                 | Teste de concorrência           |
| Assets globais | Colisões e referências inválidas    | Validador de caminhos           |



