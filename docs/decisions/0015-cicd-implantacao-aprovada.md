# ADR-0015: Automação de CI/CD com implantação manual aprovada

## Status

Aceita

## Contexto

`.github/workflows/ci.yml` hoje só faz lint, testes e build — nenhum
workflow de implantação existe, coerente com a postura de todas as
fases anteriores ("nenhum recurso AWS real é criado").
`docs/initial-architecture.md` (seção 16) prevê, eventualmente,
"implantação em ambiente de desenvolvimento" e "implantação em
produção mediante aprovação".

## Decisão

Adicionar a implantação como um workflow separado do GitHub Actions
(não misturado ao `ci.yml` existente), usando *GitHub Environments*:

- um ambiente `development`, que pode implantar automaticamente ao
  fazer merge em `main` (quando houver credenciais AWS reais
  configuradas);
- um ambiente `production`, configurado com aprovadores obrigatórios
  (*required reviewers*) — nenhuma implantação em produção roda sem
  uma pessoa clicar em aprovar na interface do GitHub.

O workflow usa `sam build`/`sam deploy` sobre o
`infra/sam/template.yaml` e os arquivos de parâmetro por ambiente já
existentes em `infra/sam/parameters/`. Até que o mantenedor forneça
credenciais AWS reais (como segredos do repositório/ambiente) e
autorize explicitamente uma primeira implantação real, este workflow
existe apenas como código revisável e não disparado — na mesma postura
que todo o `infra/` já mantém desde a Fase 1.

Adicionalmente, verificação de vulnerabilidades de dependências
(`npm audit`, `pip-audit`) é adicionada ao `ci.yml` existente — um
acréscimo de baixo risco, sem implantação, que complementa o
Dependabot já configurado (captura problemas no momento do PR, em vez
de esperar uma execução agendada do Dependabot).

## Consequências

- Nenhuma implantação real acontece como efeito colateral de mesclar o
  código desta fase — uma autorização explícita e separada (fornecer
  credenciais AWS, confirmar a conta-alvo) continua sendo necessária,
  coerente com a cautela já estabelecida em torno de mudanças de
  infraestrutura.
- Uma vez autorizado, merges em `main` poderiam implantar
  automaticamente em `development` para feedback rápido, enquanto
  `production` sempre exige aprovação humana — nenhum caminho direto
  ou automático até produção.

## Referências

- [docs/initial-architecture.md](../initial-architecture.md) — seção 16.
- [infra/sam/README.md](../../infra/sam/README.md).
- [docs/phase-4.5-plan.md](../phase-4.5-plan.md).
