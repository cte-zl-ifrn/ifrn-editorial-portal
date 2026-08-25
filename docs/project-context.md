# Contexto do projeto

Este documento resume, em um único lugar, o que já foi decidido sobre o
`ifrn-editorial-portal`, quais premissas estão sendo assumidas, quais riscos
são conhecidos e quais perguntas ainda não têm resposta. Ele não substitui o
documento de arquitetura — serve como ponto de entrada rápido antes de
consultar os detalhes.

> Estado atual: **documentação e planejamento**. Nenhuma funcionalidade foi
> implementada ainda. Não existem `frontend/`, `backend/` ou `infra/` no
> repositório neste momento, e o `.github/dependabot.yml` ainda está no
> template padrão (ecossistema não preenchido, sem workflows de CI
> configurados).

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

- Framework do frontend.
- Framework ou estilo de implementação do backend Python.
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

Antes da implantação de qualquer backend ou configuração de GitHub App em ambiente real, SECURITY.md e 
.github/dependabot.yml deverão ser revisados e configurados.


## Referências

- [README.md](../README.md)
- [SECURITY.md](../SECURITY.md) — ainda no template padrão, pendente de
  preenchimento com o processo real de reporte de vulnerabilidades.
- [docs/initial-architecture.md](initial-architecture.md)
- [docs/decisions/README.md](decisions/README.md)
- [docs/glossary.md](glossary.md)
- [docs/definition-of-done.md](definition-of-done.md)
