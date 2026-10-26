# Template SAM — Fase 1 / Fase 4.1 / Fase 4.2 / Fase 4.3 / Fase 4.5

`template.yaml` descreve a infraestrutura mínima prevista em
[ADR-0005](../../docs/decisions/0005-backend-lambda-api-gateway.md):
um API Gateway HTTP API na frente de uma função Lambda que executa o
backend (`backend/src/lambda_handler.py`). Desde a Fase 4.1, a função
também recebe o ARN do segredo do Secrets Manager como variável de
ambiente (`SECRETS_MANAGER_SECRET_ARN`) — ver
[ADR-0012](../../docs/decisions/0012-segredos-secrets-manager.md). Desde
a Fase 4.2, o template também define dois alarmes do CloudWatch
(`FunctionErrorRateAlarm`, `FunctionLatencyAlarm`) sobre as métricas
nativas `AWS/Lambda` da função — ver
[docs/phase-4.2-plan.md](../../docs/phase-4.2-plan.md). Desde a Fase
4.3, `PortalApi` define `ThrottleSettings` por rota (mais restritivo em
`POST /api/submissions`, mais permissivo nas demais) — ver
[ADR-0013](../../docs/decisions/0013-rate-limiting-api-gateway.md) e
[docs/phase-4.3-plan.md](../../docs/phase-4.3-plan.md).

**Este template não foi implantado.** Nesta fase, ele serve como
documentação executável da infraestrutura-alvo e pode ser validado
localmente com o AWS SAM CLI, sem provisionar nenhum recurso real.
Desde a Fase 4.5, `.github/workflows/deploy.yml` builda e implanta esse
template via `sam build`/`sam deploy` — mas continua sem ter sido
executado de verdade (ver "Implantação automatizada" abaixo e
[ADR-0015](../../docs/decisions/0015-cicd-implantacao-aprovada.md)).

## O que este template não faz

- Não cria o segredo do Secrets Manager — apenas referencia um ARN
  existente (`SecretsManagerSecretArn`), que deve ser criado e populado
  fora deste template, por processo institucional próprio. O segredo
  deve ser um único JSON com as quatro chaves
  `GITHUB_OAUTH_CLIENT_SECRET`, `GITHUB_APP_ID`,
  `GITHUB_APP_PRIVATE_KEY` e `SESSION_SECRET` (ver
  [ADR-0012](../../docs/decisions/0012-segredos-secrets-manager.md)) —
  o backend (`get_settings()`, `backend/src/config.py`) busca esse
  segredo uma única vez por cold start quando
  `SECRETS_MANAGER_SECRET_ARN` está presente no ambiente; sem essa
  variável (desenvolvimento local), o comportamento continua sendo
  `.env`.
- Não implanta o frontend (isso é responsabilidade do GitHub Pages/CI do
  frontend, fora do escopo desta fase).
- Não configura domínio customizado, WAF, DynamoDB, S3 ou qualquer serviço
  listado como "futuro, somente se necessário" em
  `docs/initial-architecture.md`, seção 17.
- Não conecta os alarmes do CloudWatch a nenhum canal de notificação
  real (SNS, e-mail) — os alarmes existem no template, prontos para
  avaliar as métricas, mas ninguém é avisado automaticamente ainda;
  conectar um canal depende de decidir quem deve ser notificado,
  responsabilidade institucional fora do escopo do código (ver
  [docs/phase-4.2-plan.md](../../docs/phase-4.2-plan.md)).
- Não limita por usuário ou por IP individual — o `ThrottleSettings` do
  API Gateway é por rota/estágio (granularidade grosseira), não por
  quem está fazendo a requisição; ver
  [ADR-0013](../../docs/decisions/0013-rate-limiting-api-gateway.md).
  Como todo o resto de `infra/`, só tem efeito depois de uma
  implantação real.

## Validação local (sem implantar)

Requer o [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
instalado:

```bash
sam validate --template infra/sam/template.yaml
```

## Parâmetros por ambiente

`parameters/development.json` e `parameters/production.json` contêm os
valores de parâmetro por ambiente (ver `infra/environments/`). Os valores
de produção (domínio do portal, client id de produção) são placeholders —
o domínio final do portal continua como questão em aberto (ver
`docs/project-context.md#questões-em-aberto`).

## Implantação automatizada (Fase 4.5, ADR-0015)

`.github/workflows/deploy.yml` builda e implanta via SAM, usando
*GitHub Environments* — mas **não foi executado até hoje** e não
dispara nenhuma implantação real sem configuração explícita adicional
(ver "O que este workflow não faz" abaixo). Fora do escopo desta fase:
executar o workflow de verdade, o que exige confirmação explícita e
separada do mantenedor (ver `docs/phase-1-plan.md`/`docs/phase-4-plan.md`).

### Pré-requisitos para uma implantação real (nenhum já configurado)

1. **Segredo no Secrets Manager**: criar, na conta AWS de destino, o
   segredo único com as quatro chaves sensíveis
   (`GITHUB_OAUTH_CLIENT_SECRET`, `GITHUB_APP_ID`,
   `GITHUB_APP_PRIVATE_KEY`, `SESSION_SECRET` — ver
   [ADR-0012](../../docs/decisions/0012-segredos-secrets-manager.md)) e
   preencher o ARN real em `infra/sam/parameters/<ambiente>.json`
   (hoje só têm placeholders).
2. **GitHub Environments** (Settings > Environments no repositório):
   - `development`: já criado (`gh api -X PUT
     repos/cte-zl-ifrn/ifrn-editorial-portal/environments/development`),
     sem regra de proteção — implanta automaticamente ao fazer merge
     em `main`, mas só depois do passo 4 abaixo.
   - `production`: **ainda não criado** — precisa ser criado
     manualmente, com pelo menos um *required reviewer* (aprovador
     obrigatório) configurado, antes de qualquer implantação em
     produção ser possível. Isto é uma configuração de repositório, não
     um arquivo versionado — não pôde ser feito por automação neste
     momento (ação sensível, bloqueada pelo classificador de permissões
     do Claude Code); precisa ser feito manualmente ou com autorização
     explícita adicional.
3. **Segredos/variáveis por Environment**: em cada Environment
   (`development` e, quando criado, `production`):
   - Secrets: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` (credenciais
     de uma conta/role AWS com permissão para `sam deploy` — IAM,
     Lambda, API Gateway, CloudWatch, Secrets Manager read).
   - Variables: `AWS_REGION` (ex.: `sa-east-1`).
4. **Opt-in explícito para `development` automático**: definir a
   variable `DEPLOY_DEVELOPMENT_ENABLED=true` no Environment
   `development` — sem isso, o job de deploy é **pulado** (não falha)
   em todo merge em `main`, para que a aba Actions não fique
   permanentemente vermelha antes de haver credenciais reais.
   `production` nunca dispara automaticamente, só via
   `workflow_dispatch` manual.

### O que este workflow não faz

- Não cria a conta/role AWS nem as credenciais em si — só as consome
  como segredos já configurados.
- Não implanta em `production` automaticamente, nunca — só via
  `workflow_dispatch` manual, e só depois de um aprovador confirmar
  (assim que o Environment `production` existir com essa regra).
- Não implanta `development` automaticamente até
  `DEPLOY_DEVELOPMENT_ENABLED` ser definido explicitamente como
  `"true"`.

### Rodar manualmente, sem esperar um merge

```bash
gh workflow run deploy.yml -f stage=development
gh workflow run deploy.yml -f stage=production
```

(exige as credenciais/variáveis do passo 3 já configuradas no
Environment correspondente; `production` também exige aprovação do
reviewer configurado antes de rodar).
