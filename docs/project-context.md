# Contexto do projeto

Este documento resume, em um único lugar, o que já foi decidido sobre o
`ifrn-editorial-portal`, quais premissas estão sendo assumidas, quais riscos
são conhecidos e quais perguntas ainda não têm resposta. Ele não substitui o
documento de arquitetura — serve como ponto de entrada rápido antes de
consultar os detalhes.

> Estado atual: **Fase 1, Fase 2 e Fase 3 concluídas e validadas
> manualmente** (Fase 1.5, Fase 2.1.5, Fase 2.2.5, Fase 3.1.5, Fase
> 3.2.5) — o portal já escreve de verdade no `central-ajuda`: documento
> e assets (imagens) gravados na mesma branch/Pull Request, com
> múltiplos Pull Requests de teste mergeados de verdade
> ([central-ajuda#1](https://github.com/cte-zl-ifrn/central-ajuda/pull/1),
> [#2](https://github.com/cte-zl-ifrn/central-ajuda/pull/2),
> [#3](https://github.com/cte-zl-ifrn/central-ajuda/pull/3),
> [#5](https://github.com/cte-zl-ifrn/central-ajuda/pull/5)). A
> referência de imagem gravada é uma URL absoluta do GitHub (não um
> caminho relativo — ver [ADR-0007](decisions/0007-organizacao-de-assets.md)),
> decisão tomada depois de um achado real na validação manual (caminho
> relativo divergia entre a visualização do GitHub e o site publicado
> pelo Jekyll). **Fase 4 (segurança e operação) em andamento**: dividida
> em seis sub-fases em [docs/phase-4-plan.md](phase-4-plan.md) (ver
> [issue #13](https://github.com/cte-zl-ifrn/ifrn-editorial-portal/issues/13)).
> **Fase 4.1 (segredos via AWS Secrets Manager), Fase 4.2
> (observabilidade via CloudWatch), Fase 4.3 (rate limiting e proteção
> contra abuso) e Fase 4.4 (segurança da aplicação — cabeçalhos HTTP,
> CSRF, auditoria de permissões) implementadas** — ver
> [docs/phase-4.1-plan.md](phase-4.1-plan.md),
> [docs/phase-4.2-plan.md](phase-4.2-plan.md),
> [docs/phase-4.3-plan.md](phase-4.3-plan.md) e
> [docs/phase-4.4-plan.md](phase-4.4-plan.md); pendentes apenas de uma
> implantação real (fora do escopo de qualquer fase até aqui). Ver
> [docs/phase-1-plan.md](phase-1-plan.md) e
> [docs/phase-1.5-manual-validation.md](phase-1.5-manual-validation.md)
> para a Fase 1, [docs/phase-2-plan.md](phase-2-plan.md) para a Fase 2,
> [docs/phase-3-plan.md](phase-3-plan.md) para a Fase 3, e
> [docs/phase-4-plan.md](phase-4-plan.md) para a Fase 4.

## Visão geral

O `ifrn-editorial-portal` é um portal para que usuários autorizados criem e
editem conteúdo da Central de Ajuda sem precisar conhecer Git, GitHub ou a
sintaxe Markdown. Ele não publica nada diretamente: toda alteração vira uma
proposta (branch + Pull Request) no repositório de conteúdo, que continua
responsável por revisão, build e publicação.

Para a descrição completa de objetivos, escopo, fluxos, API e roadmap, veja
[docs/initial-architecture.md](initial-architecture.md).

## Relação com o `central-ajuda`

- O portal (`cte-zl-ifrn/ifrn-editorial-portal`) e o conteúdo
  (`cte-zl-ifrn/central-ajuda`) são **repositórios separados**.
- `cte-zl-ifrn/central-ajuda` é a **única** fonte de verdade do conteúdo
  publicado e o **único** repositório que o portal está autorizado a
  alterar no MVP.
- O portal não tem lógica de negócio de publicação — quem decide o que vai
  ao ar é o processo de revisão e build do `central-ajuda`.

Detalhes em [ADR-0001](decisions/0001-separacao-portal-e-repositorio-de-conteudo.md).

## Decisões consolidadas

| # | Decisão | ADR |
|---|---|---|
| 1 | Portal separado do repositório `central-ajuda` | [0001](decisions/0001-separacao-portal-e-repositorio-de-conteudo.md) |
| 2 | Repositório de conteúdo é `cte-zl-ifrn/central-ajuda` | [0001](decisions/0001-separacao-portal-e-repositorio-de-conteudo.md) |
| 3 | Portal restrito a esse único repositório | [0001](decisions/0001-separacao-portal-e-repositorio-de-conteudo.md) |
| 4 | Editor visual: Tiptap | [0002](decisions/0002-editor-tiptap.md) |
| 5 | Armazenamento em Markdown com front matter YAML | [0003](decisions/0003-formato-markdown-front-matter.md) |
| 6 | Integração com GitHub via GitHub App | [0004](decisions/0004-integracao-github-app.md) |
| 7 | Backend inicial: AWS Lambda + API Gateway HTTP API | [0005](decisions/0005-backend-lambda-api-gateway.md) |
| 8 | Cada alteração cria branch e Pull Request | [0006](decisions/0006-fluxo-branch-e-pull-request.md) |
| 9 | Sem push direto na `main` | [0006](decisions/0006-fluxo-branch-e-pull-request.md) |
| 10 | Imagens em `assets/images`, arquivos em `assets/files` | [0007](decisions/0007-organizacao-de-assets.md) |
| 11 | Frontend em Vue 3, TypeScript e Vite | [0008](decisions/0008-frontend-vue-3.md) |
| 12 | Front matter preservado como texto bruto; parsing Markdown→Tiptap com parser controlado; serializer Tiptap→Markdown próprio | [0009](decisions/0009-conversao-markdown-tiptap-e-front-matter.md) |
| 13 | Backend implementado com FastAPI (não Django) | [0010](decisions/0010-backend-fastapi.md) |
| 14 | Gravação via Contents API (não Git Data API); conflito revalidado antes de gravar; front matter sempre relido, nunca confiado ao cliente; idempotência best-effort | [0011](decisions/0011-escrita-branch-commit-pull-request.md) |
| 15 | Segredos de produção em um único segredo JSON no AWS Secrets Manager, buscado uma vez por cold start | [0012](decisions/0012-segredos-secrets-manager.md) |
| 16 | Rate limiting via throttling nativo do API Gateway, não um limitador de aplicação com estado compartilhado | [0013](decisions/0013-rate-limiting-api-gateway.md) |
| 17 | CSRF em requisições autenticadas por cookie cross-origin mitigado por cabeçalho customizado exigido, não por token armazenado | [0014](decisions/0014-csrf-cookies-cross-origin.md) |
| 18 | Implantação automática em `development`, aprovação humana obrigatória em `production` | [0015](decisions/0015-cicd-implantacao-aprovada.md) |

O índice completo, com contexto e consequências de cada decisão, está em
[docs/decisions/README.md](decisions/README.md).

## Premissas assumidas

- Existe pelo menos um mantenedor com permissão administrativa no
  `central-ajuda` para instalar a GitHub App e configurar proteção de
  branch.
- Usuários finais possuem conta GitHub e permissão (`write`, `maintain` ou
  `admin`) no repositório `central-ajuda`.
- O gerador de site do `central-ajuda` continua sendo o Jekyll durante o
  MVP; o design deve permitir trocá-lo no futuro, mas isso não é feito
  agora.
- Não haverá banco de dados como fonte de verdade do conteúdo no MVP; o
  estado necessário é reconstruível a partir de Pull Requests, commits e
  branches.
- A revisão e o merge dos Pull Requests continuam sendo feitos por humanos
  no `central-ajuda`; o portal não implementa aprovação editorial completa.
- O ambiente AWS (conta, orçamento, política de nuvem) está disponível para
  hospedar o backend serverless; caso não esteja, a decisão registrada em
  [ADR-0005](decisions/0005-backend-lambda-api-gateway.md) precisa ser
  revisitada.

## Riscos conhecidos

| Risco | Impacto | Mitigação prevista |
|---|---|---|
| Conversão imperfeita Tiptap ↔ Markdown | Alto | Modelo de nós controlado e testes de round-trip |
| Token ou credencial exposta no frontend | Alto | Toda operação privilegiada roda no backend |
| Gravação em caminho indevido do repositório | Alto | Caminhos gerados e validados pelo backend, nunca informados livremente pelo usuário |
| Conflito de edição concorrente | Médio | Verificação de versão (`base_sha`) antes de gravar |
| Upload malicioso (imagem ou arquivo) | Alto | Validação de MIME type, assinatura, extensão, tamanho e sanitização |
| Dependência excessiva do modelo do GitHub | Médio | Camada de adaptação e modelo editorial próprio |
| Custos AWS não monitorados | Médio | Budgets, métricas e limites de uso |
| Dados pessoais expostos em Pull Requests | Médio | Template de PR e política de dados controlados |
| Complexidade prematura (banco de dados, múltiplos repositórios) | Médio | MVP deliberadamente sem essas capacidades |

Descrição completa em
[docs/initial-architecture.md, seção 22](initial-architecture.md#22-riscos).

## Questões em aberto

Ainda não decididas — não devem ser assumidas como resolvidas ao planejar
trabalho futuro:

- Método exato de autenticação do usuário (OAuth com PKCE vs. fluxo de
  instalação associado à GitHub App).
- Lista final de permissões por papel de usuário.
- Categorias oficiais de documentos.
- Campos obrigatórios definitivos do front matter.
- Extensões e limites de tamanho de arquivos permitidos.
- Domínio do portal.
- Estratégia de CORS e cookies entre GitHub Pages e a API.
- Existência (ou não) de um ambiente de homologação.
- Método de prévia do Pull Request antes do merge.
- Política institucional de retenção de logs (LGPD).
- Responsável institucional por revisar e aprovar os Pull Requests.

Quando qualquer uma dessas questões for resolvida, registre a decisão como
uma nova ADR em [docs/decisions/](decisions/) em vez de apenas atualizar
este documento.

## Sobre SECURITY.md e .github/dependabot.yml

Atualizados na Fase 1: `SECURITY.md` descreve o canal de reporte de
vulnerabilidades (GitHub Security Advisories) e a superfície de segurança
introduzida pelo backend (sessão, GitHub App, segredos); `.github/dependabot.yml`
passou do template vazio para monitorar os três ecossistemas reais
(`npm` em `/frontend`, `pip` em `/backend`, `github-actions` em `/`). Ambos
devem ser revisados novamente antes de qualquer implantação real em
produção (contato institucional definitivo, políticas de retenção etc.).


## Referências

- [README.md](../README.md)
- [SECURITY.md](../SECURITY.md) — canal de reporte de vulnerabilidades e
  superfície de segurança da Fase 1.
- [docs/initial-architecture.md](initial-architecture.md)
- [docs/decisions/README.md](decisions/README.md)
- [docs/glossary.md](glossary.md)
- [docs/definition-of-done.md](definition-of-done.md)
- [docs/phase-1-plan.md](phase-1-plan.md)
- [docs/phase-1.5-manual-validation.md](phase-1.5-manual-validation.md)
- [docs/phase-2-plan.md](phase-2-plan.md)
- [docs/phase-2.1-plan.md](phase-2.1-plan.md)
- [docs/phase-2.1.5-manual-validation.md](phase-2.1.5-manual-validation.md)
- [docs/phase-2.2-plan.md](phase-2.2-plan.md)
- [docs/phase-2.2.5-manual-validation.md](phase-2.2.5-manual-validation.md)
- [docs/phase-3-plan.md](phase-3-plan.md)
- [docs/phase-3.1-plan.md](phase-3.1-plan.md)
- [docs/phase-3.1.5-manual-validation.md](phase-3.1.5-manual-validation.md)
- [docs/phase-3.2-plan.md](phase-3.2-plan.md)
- [docs/phase-3.2.5-manual-validation.md](phase-3.2.5-manual-validation.md)
- [docs/phase-4-plan.md](phase-4-plan.md)
- [docs/phase-4.1-plan.md](phase-4.1-plan.md)
- [docs/phase-4.2-plan.md](phase-4.2-plan.md)
- [docs/phase-4.3-plan.md](phase-4.3-plan.md)
- [docs/phase-4.4-plan.md](phase-4.4-plan.md)
- [docs/phase-4.5-plan.md](phase-4.5-plan.md)
- [docs/phase-4.6-plan.md](phase-4.6-plan.md)
- [docs/requirements/functional-requirements.md](requirements/functional-requirements.md)
- [docs/requirements/non-functional-requirements.md](requirements/non-functional-requirements.md)
- [docs/requirements/user-stories.md](requirements/user-stories.md)
- [docs/architecture/system-context.md](architecture/system-context.md)
- [docs/architecture/authentication-flow.md](architecture/authentication-flow.md)
- [docs/architecture/authorization-model.md](architecture/authorization-model.md)
- [docs/api/openapi.yaml](api/openapi.yaml)
