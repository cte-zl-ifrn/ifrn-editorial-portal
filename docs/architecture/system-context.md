# Contexto do sistema — Fase 1

Este documento descreve os componentes envolvidos no caminho crítico de
leitura da Fase 1 e suas responsabilidades. Para a arquitetura completa do
projeto (incluindo edição, upload e submissão), ver
[docs/initial-architecture.md](../initial-architecture.md).

## Diagrama de contexto

```text
+------------------------+
| Usuário autorizado     |
+-----------+------------+
            |
            | HTTPS
            v
+------------------------+
| Frontend (Vue 3)       |
| GitHub Pages (build)   |
| Executado localmente   |
| via Vite nesta fase    |
+-----------+------------+
            |
            | HTTPS, cookie de sessão (credentials: include)
            v
+------------------------+
| Backend                |
| API Gateway HTTP API    |
| + AWS Lambda (Python)  |
| (executado localmente  |
| nesta fase)            |
+---+-------+--------+---+
    |       |        |
    |       |        +----------------------+
    |       v                               v
    |  Secrets/variáveis              Logs estruturados
    |  de ambiente (dev)              (stdout/CloudWatch)
    |  GitHub OAuth App +
    |  GitHub App (chave privada)
    |
    v
+------------------------+
| GitHub                 |
| - OAuth (identidade)   |
| - GitHub App (leitura) |
+-----------+------------+
            |
            v
+------------------------+
| cte-zl-ifrn/            |
| central-ajuda           |
| (somente leitura        |
| nesta fase)             |
+------------------------+
```

## Componentes

### Frontend (`frontend/`)

- Aplicação Vue 3 + TypeScript + Vite (ver
  [ADR-0008](../decisions/0008-frontend-vue-3.md)).
- Responsável por: iniciar o login (redirecionando para o backend),
  exibir estados de carregamento/erro, consumir `GET /api/me` e
  `GET /api/documents/sample`, exibir o conteúdo do documento.
- Não contém nenhuma credencial privilegiada, nem lógica de autorização —
  apenas reflete o que o backend retorna.
- Nesta fase, é executado localmente via `npm run dev`; o build de
  produção (`npm run build`) é validado, mas a publicação real no GitHub
  Pages não faz parte do escopo.

### Backend (`backend/`)

- Implementado em Python, com handlers pensados para AWS Lambda (ver
  [ADR-0005](../decisions/0005-backend-lambda-api-gateway.md)), mas
  executáveis localmente nesta fase (sem exigir AWS real).
- Responsável por: health check, fluxo OAuth (login/callback), sessão,
  `/api/me`, verificação de autorização, obtenção de installation access
  token da GitHub App, leitura de conteúdo do repositório fixo.
- É o único componente que conhece segredos (client secret OAuth, chave
  privada da GitHub App) e que fala diretamente com a API do GitHub.

### GitHub (identidade e conteúdo)

- **OAuth App/fluxo OAuth do GitHub**: usado para autenticar a pessoa
  usuária e obter sua identidade (login, id, nome, avatar) e, quando
  necessário, sua permissão no repositório.
- **GitHub App**: instalada em `cte-zl-ifrn/central-ajuda`, usada pelo
  backend para ler o conteúdo do repositório com uma identidade técnica
  própria, sem depender do token do usuário para essa leitura (ver
  [docs/architecture/authentication-flow.md](authentication-flow.md) para a
  distinção entre as duas identidades).

### Repositório de conteúdo (`cte-zl-ifrn/central-ajuda`)

- Único repositório acessado nesta fase, somente para leitura.
- `owner`, `repo` e `branch` (`cte-zl-ifrn` / `central-ajuda` / `main`) são
  fixos no backend (ver [ADR-0001](../decisions/0001-separacao-portal-e-repositorio-de-conteudo.md)).

## Fronteira entre frontend e backend

- O frontend nunca chama a API do GitHub diretamente. Toda comunicação com
  o GitHub passa pelo backend.
- O frontend se comunica com o backend por HTTPS, enviando o cookie de
  sessão (`credentials: "include"`), sem manipular tokens diretamente.
- A URL base da API é configurada no frontend por variável de ambiente
  (`VITE_API_BASE_URL` — ver `frontend/README.md`), nunca hardcoded.

## Relação com a GitHub App

- A GitHub App é instalada exclusivamente em
  `cte-zl-ifrn/central-ajuda`, com permissões `Contents: Read-only` e
  `Metadata: Read-only` nesta fase (ver
  [docs/api/openapi.yaml](../api/openapi.yaml) e a nota de escopo em
  [docs/phase-1-plan.md](../phase-1-plan.md)). Permissões de escrita
  (`Contents`/`Pull requests`) só serão solicitadas quando as fases de
  submissão forem implementadas, conforme já previsto em
  [ADR-0004](../decisions/0004-integracao-github-app.md).

## Limites da Fase 1

- Nenhuma escrita no `central-ajuda`: sem commits, branches ou Pull
  Requests.
- Nenhum banco de dados: o estado da sessão vive em memória/cookie assinado
  para esta fase (ver `backend/README.md` para detalhes de implementação).
- Nenhuma infraestrutura AWS real provisionada: `infra/` contém apenas
  templates e documentação.
- Um único documento de demonstração
  (`_docs/ambiente-virtual/acesso-moodle.md`) é exposto via
  `/api/documents/sample`; não há listagem geral de documentos nesta fase.
