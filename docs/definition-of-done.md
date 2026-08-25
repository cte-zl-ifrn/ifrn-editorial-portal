# Definition of Done

Critérios mínimos para considerar uma alteração concluída no
`ifrn-editorial-portal`. O projeto está na fase de documentação e
planejamento (ver [docs/project-context.md](project-context.md)), então os
critérios abaixo cobrem tanto o estado atual (documentação e decisões)
quanto o que passa a valer assim que a implementação começar.

## Regras gerais, sempre válidas

Uma alteração só é considerada concluída quando:

- [ ] Segue as decisões já registradas em [docs/decisions/](decisions/README.md).
      Se contradiz uma ADR existente, uma nova ADR é criada explicando a
      mudança antes (ou junto) da implementação.
- [ ] Não inclui push direto na branch `main` do repositório
      `cte-zl-ifrn/central-ajuda` — toda alteração de conteúdo chega por
      branch própria e Pull Request (ver
      [ADR-0006](decisions/0006-fluxo-branch-e-pull-request.md)).
- [ ] Não introduz caminhos de gravação fora de `_docs/`, `assets/images/`
      ou `assets/files/` no repositório de conteúdo.
- [ ] Não expõe segredos, tokens, chaves privadas ou credenciais AWS em
      código, logs, commits ou no bundle do frontend.
- [ ] Atualiza a documentação afetada (`docs/initial-architecture.md`,
      `docs/project-context.md`, `docs/glossary.md` ou uma ADR) quando a
      alteração muda escopo, decisão ou vocabulário do projeto.
- [ ] Não implementa itens listados como "fora do MVP" na seção 3 de
      [docs/initial-architecture.md](initial-architecture.md) sem uma
      decisão explícita que mude esse escopo.

## Para alterações de documentação (fase atual)

- [ ] O documento novo ou alterado está linkado a partir de pelo menos um
      outro documento relevante (por exemplo, `project-context.md` ou o
      índice de ADRs), para não ficar órfão.
- [ ] Termos novos usados no documento existem em
      [docs/glossary.md](glossary.md), ou o glossário é atualizado junto.
- [ ] Decisões de arquitetura ou produto novas viram uma ADR em
      [docs/decisions/](decisions/README.md), não apenas um parágrafo solto
      em outro arquivo.
- [ ] Riscos e questões em aberto identificados durante a discussão são
      registrados em [docs/project-context.md](project-context.md), não
      apenas mencionados em conversa.
- [ ] Links internos entre documentos Markdown foram verificados (o arquivo
      e a âncora referenciados existem).

## Para alterações de código (quando a implementação começar)

Além das regras gerais:

- [ ] Testes automatizados cobrem o comportamento alterado, incluindo casos
      de erro esperados pela arquitetura (permissão negada, conflito de
      versão, upload inválido, front matter inválido).
- [ ] Validações de segurança descritas na seção 14 de
      `docs/initial-architecture.md` continuam sendo aplicadas (CORS,
      CSRF, tamanho de upload, tipos/extensões, path traversal, CSP).
- [ ] Nenhuma permissão nova é solicitada à GitHub App além das listadas em
      [ADR-0004](decisions/0004-integracao-github-app.md), sem atualizar a
      ADR correspondente.
- [ ] Eventos relevantes são registrados em log sem dados sensíveis (ver
      seção 19 de `docs/initial-architecture.md`), com `correlation_id`.
- [ ] Lint, formatação e verificação de dependências passam localmente ou
      no pipeline de CI configurado.
- [ ] A alteração foi validada manualmente contra os critérios de aceite do
      MVP aplicáveis (seção 23 de `docs/initial-architecture.md`), quando
      tocar um desses fluxos.

## Para Pull Requests no repositório do portal

- [ ] Descrição do PR explica o "porquê" da mudança, não só o "o quê".
- [ ] Referencia a ADR ou seção da arquitetura relacionada, quando aplicável.
- [ ] Não mistura, no mesmo PR, decisão de arquitetura e implementação de
      funcionalidade não relacionada.
