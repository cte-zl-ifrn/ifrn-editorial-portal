# ADR-0010: Backend implementado com FastAPI (não Django)

## Status

Aceita

## Contexto

[ADR-0005](0005-backend-lambda-api-gateway.md) já decidiu que o backend
roda em AWS Lambda por trás de um API Gateway HTTP API, mas não fixava o
framework Python usado para estruturar rotas, validação e testes. O
documento de arquitetura inicial (`docs/initial-architecture.md`, seção
6.2) já cogitava "Python com FastAPI adaptado para Lambda, ou handlers
Lambda mais diretos" como opções, sem decidir entre elas. Essa lacuna
ficou registrada como questão em aberto ("framework ou estilo de
implementação do backend Python") em `docs/project-context.md`, mas já
havia sido resolvida na prática desde a implementação da Fase 1
(`backend/src/app.py`), sem nunca ter sido formalizada como ADR.

## Decisão

O backend usa **FastAPI**, com **Mangum** como adaptador para AWS Lambda
(`backend/src/lambda_handler.py`), sem introduzir Django.

### Alternativas consideradas

| Alternativa | Motivo de não adoção |
|---|---|
| Django (+ Django REST Framework) | Traz ORM, admin e app registry que o projeto não usa — a Fase 1 é deliberadamente sem banco de dados (ADR-0005). Peso e convenções desnecessários para uma API somente-serverless. |
| Handlers Lambda diretos, sem framework | Reimplementaria roteamento, parsing de cookies/query params, validação de payload e um cliente de testes por conta própria — todo o valor que um micro-framework já resolve. |
| Flask | Viável, mas sem tipagem/validação nativa via Pydantic nem geração implícita de esquemas — exigiria bibliotecas adicionais para chegar ao mesmo nível de garantias que o FastAPI já oferece de fábrica. |

### Por que FastAPI

- Tipagem e validação de entrada/saída via Pydantic (`backend/src/models/`),
  incluindo a normalização de configuração sensível (ex.: chave privada da
  GitHub App, ver `backend/src/config.py`).
- `TestClient` (via Starlette/httpx) permite testar os handlers como
  requisições HTTP reais, sem subir um servidor (`backend/tests/`).
- `Mangum` é um adaptador maduro e simples para expor uma aplicação ASGI
  como handler de Lambda atrás de um API Gateway HTTP API, coerente com
  ADR-0005.
- Suporte nativo a documentação OpenAPI, usada como referência cruzada
  com a especificação mantida manualmente em `docs/api/openapi.yaml`.

## Consequências

- O backend depende de Starlette, Pydantic e Mangum como dependências
  centrais (ver `backend/requirements.txt`) — atualizações dessas
  bibliotecas passam pelo Dependabot (`pip` em `/backend`, ver
  `.github/dependabot.yml`).
- Qualquer futura necessidade de funcionalidades típicas de um framework
  full-stack (admin, ORM, migrations) exigiria reabrir esta decisão; não é
  esperado que isso aconteça enquanto o projeto permanecer sem banco de
  dados.
- Resolve a questão em aberto "framework ou estilo de implementação do
  backend Python" — removida de `docs/project-context.md`.

## Referências

- [ADR-0005](0005-backend-lambda-api-gateway.md) — Lambda + API Gateway HTTP API.
- [docs/initial-architecture.md](../initial-architecture.md) — seção 6.2.
- [backend/README.md](../../backend/README.md) — detalhes de execução local.
