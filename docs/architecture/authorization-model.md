# Modelo de autorização — Fase 1

Este documento descreve como o backend decide se um usuário autenticado
pode usar o portal, e como isso se relaciona com as permissões da GitHub
App. Para o fluxo de autenticação em si, ver
[docs/architecture/authentication-flow.md](authentication-flow.md).

## Duas autorizações independentes

1. **Autorização do usuário para usar o portal** — calculada a partir da
   permissão efetiva do usuário autenticado no repositório
   `cte-zl-ifrn/central-ajuda`.
2. **Autorização da GitHub App para ler o repositório** — concedida uma
   única vez, na instalação da GitHub App em `cte-zl-ifrn/central-ajuda`,
   e independente de qual usuário está usando o portal no momento.

O backend nunca deve inferir a autorização do usuário a partir da
autorização da GitHub App (a GitHub App sempre pode ler o repositório onde
está instalada, independentemente de quem está logado no portal). A
verificação de permissão do usuário é sempre feita explicitamente.

## Regra de autorização do usuário (Fase 1)

| Permissão GitHub no `central-ajuda` | Resultado |
|---|---|
| Nenhum acesso | Não autorizado |
| `read` | Não autorizado |
| `triage` | Não autorizado |
| `write` | **Autorizado** |
| `maintain` | **Autorizado** |
| `admin` | **Autorizado** |

Esta regra segue a sugestão inicial do MVP descrita na seção 7.2 de
[docs/initial-architecture.md](../initial-architecture.md): "A implementação
do MVP pode permitir apenas usuários com permissão `write`, `maintain` ou
`admin` para operações editoriais." Como a Fase 1 não realiza nenhuma
operação editorial de escrita, a mesma regra é aplicada de forma
conservadora também à leitura do documento de exemplo, para validar o
caminho de autorização com a regra final já prevista, em vez de uma regra
mais permissiva que precisaria ser revisitada depois.

A lista de papéis por permissão (tabela completa da seção 7.2) continua
como questão em aberto para refinamento futuro — ver
`docs/project-context.md#questões-em-aberto`.

## Como a permissão é verificada

O backend consulta a API do GitHub para obter a permissão do usuário
autenticado no repositório `cte-zl-ifrn/central-ajuda` (endpoint de
permissão de colaborador). Essa consulta pode ser feita:

- usando o token de acesso do usuário obtido no OAuth (se o escopo
  concedido permitir), ou
- usando o installation access token da GitHub App para consultar a
  permissão do usuário (evitando exigir escopos adicionais no OAuth do
  usuário).

A escolha entre essas duas abordagens é um detalhe de implementação do
backend (documentado em `backend/README.md`) — ambas resultam no mesmo
modelo de autorização descrito aqui.

## Onde a verificação é aplicada

- `GET /api/me`: sempre retorna o resultado da verificação de autorização
  junto com a identidade do usuário (autorizado ou não), para que o
  frontend possa decidir qual tela mostrar.
- `GET /api/documents/sample`: exige sessão válida **e** usuário autorizado.
  Se o usuário estiver autenticado mas não autorizado, o backend responde
  HTTP 403 sem consultar ou retornar o conteúdo do documento.

## O que este modelo não cobre nesta fase

- Papéis internos do portal (ex.: "revisor", "administrador do portal")
  distintos da permissão no repositório GitHub — não existem nesta fase.
- Autorização por documento ou por categoria — nesta fase, a autorização é
  binária e vale para o repositório inteiro.
- Cache de permissão entre requisições — cada verificação é recalculada;
  otimizações de cache ficam para fases futuras, se necessário.
