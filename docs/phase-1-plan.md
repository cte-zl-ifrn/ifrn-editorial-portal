# Plano da Fase 1 — Spike do caminho crítico de leitura

## Objetivo

Validar, de ponta a ponta, o caminho crítico somente de leitura do portal:

```text
frontend Vue
  → backend
  → autenticação GitHub
  → autorização no repositório
  → GitHub App
  → leitura de um arquivo Markdown
```

Ao final da fase, um usuário autorizado deve conseguir autenticar-se, ser
reconhecido pelo backend, ter sua permissão verificada no repositório
`cte-zl-ifrn/central-ajuda` e visualizar o conteúdo de um documento Markdown
real, sem que nenhuma escrita ocorra nesse repositório.

## Justificativa

O documento de arquitetura inicial ([docs/initial-architecture.md](initial-architecture.md))
já descreve o sistema completo, incluindo edição, upload e submissão via
Pull Request. Esses fluxos dependem de decisões que só podem ser validadas
na prática: autenticação real com o GitHub, obtenção de um installation
access token da GitHub App e leitura de conteúdo real do repositório de
conteúdo.

Construir esse caminho primeiro, isoladamente, permite:

- validar a integração de autenticação e sessão antes de acoplar o editor;
- confirmar que a GitHub App consegue ler o repositório com permissões
  mínimas, antes de solicitar qualquer permissão de escrita;
- expor cedo problemas de CORS, cookies entre GitHub Pages e a API, e
  configuração de ambiente;
- reduzir o risco de descobrir, tarde, que uma premissa de autenticação ou
  autorização estava errada.

## Escopo

Ver a lista completa em
[README.md](../README.md) e no pedido que originou esta fase. Resumo do que
é implementado:

1. Documentação da Fase 1 (este documento e os demais em
   `docs/requirements/`, `docs/architecture/` e `docs/api/`).
2. [ADR-0008](decisions/0008-frontend-vue-3.md) — adoção de Vue 3.
3. Esqueleto do frontend Vue 3 + TypeScript + Vite (`frontend/`).
4. Esqueleto do backend Python (`backend/`).
5. Endpoint de saúde (`GET /health`).
6. Fluxo inicial de autenticação (`GET /auth/login`, `GET /auth/callback`).
7. Criação de sessão segura (cookie `HttpOnly`, `Secure`, `SameSite`).
8. Endpoint `GET /api/me`.
9. Verificação da permissão do usuário no repositório
   `cte-zl-ifrn/central-ajuda`.
10. Integração de leitura da GitHub App (JWT da aplicação + installation
    access token, permissões somente leitura).
11. Endpoint `GET /api/documents/sample`, lendo
    `_docs/ambiente-virtual/acesso-moodle.md` no `central-ajuda`.
12. Infraestrutura mínima para execução local (`infra/sam/template.yaml` e
    documentação de ambiente local).
13. Testes automatizados essenciais (backend com pytest, frontend com
    Vitest).
14. CI mínimo (lint, testes e build do frontend; testes do backend;
    verificação de arquivos sensíveis).

## Fora do escopo

Não fazem parte da Fase 1 (ver também a seção 3 "Fora do MVP" de
`docs/initial-architecture.md`):

- edição Tiptap e conversão Tiptap ↔ Markdown;
- upload de imagens ou arquivos;
- criação de branches, commits ou Pull Requests no `central-ajuda`;
- publicação de conteúdo;
- banco de dados ou rascunhos persistentes;
- suporte a múltiplos repositórios;
- integração com SUAP, LDAP ou outro provedor de identidade institucional;
- administração editorial ou edição colaborativa;
- implantação em infraestrutura AWS real (a Fase 1 entrega templates e
  execução local, não recursos provisionados).

## Entregáveis

| Entregável | Local |
|---|---|
| Plano da fase | `docs/phase-1-plan.md` |
| Requisitos funcionais | `docs/requirements/functional-requirements.md` |
| Requisitos não funcionais | `docs/requirements/non-functional-requirements.md` |
| Histórias de usuário | `docs/requirements/user-stories.md` |
| Contexto do sistema | `docs/architecture/system-context.md` |
| Fluxo de autenticação | `docs/architecture/authentication-flow.md` |
| Modelo de autorização | `docs/architecture/authorization-model.md` |
| Especificação OpenAPI | `docs/api/openapi.yaml` |
| ADR de adoção do Vue 3 | `docs/decisions/0008-frontend-vue-3.md` |
| Frontend | `frontend/` |
| Backend | `backend/` |
| Infraestrutura mínima | `infra/` |
| CI | `.github/workflows/` |

## Sequência de execução

1. Documentar decisões e requisitos antes de escrever código (este
   conjunto de documentos).
2. Esqueleto do backend: configuração, health check, logging estruturado.
3. Fluxo de autenticação: login, callback, sessão, `/api/me`.
4. Integração de leitura com a GitHub App: JWT, installation access token,
   leitura de conteúdo, decodificação Base64.
5. Autorização: verificação de permissão do usuário autenticado no
   repositório fixo.
6. Endpoint de leitura de documento (`/api/documents/sample`).
7. Esqueleto do frontend: estrutura de rotas, estados de tela, serviços de
   API, consumo de `/api/me` e `/api/documents/sample`.
8. Infraestrutura mínima (SAM) e documentação de execução local.
9. Testes automatizados (backend e frontend).
10. CI (lint, testes, build).
11. Atualização final da documentação (glossário, contexto do projeto,
    índice de ADRs, `SECURITY.md`, `dependabot.yml`).

## Riscos

| Risco | Impacto | Mitigação nesta fase |
|---|---|---|
| Complexidade de autenticação e cookies entre GitHub Pages e a API (CORS, `SameSite`) | Alto | Validar localmente com backend e frontend em origens diferentes; documentar a configuração exigida em `docs/architecture/authentication-flow.md` |
| Geração incorreta do JWT da GitHub App ou expiração do installation access token | Alto | Testes unitários com mocks da API do GitHub; tratamento explícito de erro de autenticação com a GitHub App |
| Confusão entre autenticação do usuário e identidade da GitHub App | Médio | Documentado explicitamente em `docs/architecture/authentication-flow.md` e no glossário |
| Vazamento de segredo em log ou commit | Alto | Checklist de CI para arquivos sensíveis; segredos somente via variável de ambiente/Secrets Manager, nunca versionados |
| Permissão do usuário no repositório calculada incorretamente | Alto | Testes cobrindo `write`/`maintain`/`admin` (autorizado) e permissões inferiores (não autorizado) |
| Caminho do documento de exemplo se tornar inválido (arquivo renomeado/removido no `central-ajuda`) | Médio | Caminho documentado explicitamente nesta fase; endpoint trata arquivo inexistente com erro claro |

Ver também a tabela de riscos consolidada em
[docs/project-context.md](project-context.md#riscos-conhecidos).

## Critérios de aceite

A Fase 1 é considerada concluída quando:

- o frontend Vue compila (`npm run build` sem erros);
- o backend responde ao health check (`GET /health`) sem exigir
  autenticação nem acessar o GitHub;
- a documentação da fase (este conjunto de arquivos) está completa e
  consistente com o restante de `docs/`;
- a [ADR-0008](decisions/0008-frontend-vue-3.md) está criada e indexada em
  `docs/decisions/README.md`;
- não há referência a React, Next.js ou outro framework de frontend como
  padrão do projeto em nenhum documento;
- o login está documentado e funcional no ambiente de desenvolvimento local
  (com credenciais de teste/mock, conforme `backend/README.md`);
- a sessão é protegida (cookie `HttpOnly`, `Secure`, `SameSite`, expiração
  curta);
- `GET /api/me` retorna a identidade do usuário autenticado, ou erro
  apropriado se não houver sessão válida;
- um usuário sem permissão compatível no repositório recebe uma resposta de
  não autorizado e não consegue ler `/api/documents/sample`;
- o backend rejeita qualquer tentativa de alterar `owner`, `repo` ou
  `branch` por parâmetro de requisição — esses valores são fixos em
  `cte-zl-ifrn` / `central-ajuda` / `main`;
- a GitHub App consegue ler o conteúdo permitido usando apenas permissões
  `Contents: Read-only` e `Metadata: Read-only`;
- o arquivo `_docs/ambiente-virtual/acesso-moodle.md` do `central-ajuda`
  pode ser consultado via `/api/documents/sample`, retornando `path`,
  `name`, `content`, `sha` e `encoding`;
- nenhum commit, branch ou Pull Request é criado no `central-ajuda`;
- nenhum segredo aparece no frontend, nos logs do backend ou no
  repositório do portal;
- os testes automatizados definidos (backend e frontend) executam com
  sucesso localmente e no CI;
- a execução local está documentada em `backend/README.md`,
  `frontend/README.md` e `infra/README.md`;
- as limitações e decisões em aberto desta fase estão registradas neste
  documento e em `docs/project-context.md`.

## Dependências

- Acesso de leitura (via `gh api`, usado apenas para investigação e
  validação de documentação) ao repositório `cte-zl-ifrn/central-ajuda`
  para confirmar caminhos reais de conteúdo.
- Disponibilidade de Node.js/npm e Python no ambiente de desenvolvimento.
- Uma GitHub App real só é necessária para testar o fluxo fim a fim contra
  o GitHub de verdade; o desenvolvimento e os testes automatizados locais
  usam mocks/fixtures da API do GitHub (ver `backend/README.md`).
- Nenhuma dependência de infraestrutura AWS real nesta fase — os templates
  em `infra/` não são implantados.

## Decisões em aberto (específicas da Fase 1)

- Provedor de OAuth: usar o fluxo OAuth padrão do GitHub (`login/oauth/authorize`)
  associado à identificação do usuário, com a GitHub App usada
  separadamente para as chamadas de leitura ao repositório. A escolha entre
  OAuth com PKCE ou um fluxo alternativo de instalação continua em aberto
  (ver `docs/project-context.md`) e não bloqueia esta fase, que pode operar
  com o fluxo OAuth tradicional de aplicação web do GitHub.
- Provedor de secret store em desenvolvimento local: variáveis de ambiente
  (`.env`, não versionado) simulam o AWS Secrets Manager, que só é usado
  quando houver implantação real.
- Domínio final do portal, estratégia definitiva de CORS/cookies em
  produção e ambiente de homologação continuam como questões em aberto do
  projeto (ver `docs/project-context.md#questões-em-aberto`) — a Fase 1
  documenta e valida a configuração necessária apenas para desenvolvimento
  local.

## Definição de pronto da fase

Uma tarefa da Fase 1 só é considerada pronta quando satisfizer também a
[Definition of Done](definition-of-done.md) geral do projeto, além dos
critérios de aceite acima. Nenhuma tarefa desta fase deve ser marcada como
concluída sem os testes correspondentes executados com sucesso.
