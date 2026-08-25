# Template SAM — Fase 1

`template.yaml` descreve a infraestrutura mínima prevista em
[ADR-0005](../../docs/decisions/0005-backend-lambda-api-gateway.md):
um API Gateway HTTP API na frente de uma função Lambda que executa o
backend (`backend/src/lambda_handler.py`).

**Este template não foi implantado.** Nesta fase, ele serve como
documentação executável da infraestrutura-alvo e pode ser validado
localmente com o AWS SAM CLI, sem provisionar nenhum recurso real.

## O que este template não faz

- Não cria o segredo do Secrets Manager — apenas referencia um ARN
  existente (`SecretsManagerSecretArn`), que deve ser criado e populado
  fora deste template, por processo institucional próprio.
- Não implanta o frontend (isso é responsabilidade do GitHub Pages/CI do
  frontend, fora do escopo desta fase).
- Não configura domínio customizado, WAF, DynamoDB, S3 ou qualquer serviço
  listado como "futuro, somente se necessário" em
  `docs/initial-architecture.md`, seção 17.

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

## Implantação real (fora do escopo desta fase)

Uma eventual implantação real exigiria, no mínimo:

1. confirmação explícita para provisionar recursos AWS (ver
   `docs/phase-1-plan.md`, que proíbe isso nesta fase);
2. criação do segredo no Secrets Manager com os valores sensíveis
   (`GITHUB_OAUTH_CLIENT_SECRET`, `GITHUB_APP_ID`,
   `GITHUB_APP_PRIVATE_KEY`, `SESSION_SECRET`);
3. `sam build --template infra/sam/template.yaml`;
4. `sam deploy --parameter-overrides file://infra/sam/parameters/<ambiente>.json ...`.
