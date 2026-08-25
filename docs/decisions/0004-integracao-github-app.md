# ADR-0004: Integração com o GitHub via GitHub App

## Status

Aceita

## Contexto

O portal precisa ler e gravar conteúdo no repositório `central-ajuda` e criar
Pull Requests em nome do sistema, sem depender de tokens pessoais de
administrador e sem expor credenciais privilegiadas no navegador.

## Decisão

A integração com o GitHub usará uma GitHub App, instalada exclusivamente no
repositório `cte-zl-ifrn/central-ajuda`, com permissões mínimas:

| Recurso | Permissão | Motivo |
|---|---|---|
| Contents | Read and write | Ler e gravar documentos e assets |
| Pull requests | Read and write | Criar e consultar Pull Requests |
| Metadata | Read-only | Consultar informações básicas |

O backend gera um JWT da aplicação e solicita um installation access token
de curta duração para cada operação. Nenhum token ou chave privada é
persistido ou exposto no frontend.

## Consequências

- Não devem ser solicitadas permissões de workflows, administração da
  organização, usuários, secrets ou deployments no MVP.
- A chave privada da GitHub App deve ficar no AWS Secrets Manager (ver
  [ADR-0005](0005-backend-lambda-api-gateway.md)).
- O método exato de autenticação do usuário final (OAuth com PKCE vs. fluxo
  de instalação) permanece como questão em aberto (ver
  [docs/project-context.md](../project-context.md#questões-em-aberto)).

## Referências

- [docs/initial-architecture.md](../initial-architecture.md) — seções 6.3, 7, 14.
