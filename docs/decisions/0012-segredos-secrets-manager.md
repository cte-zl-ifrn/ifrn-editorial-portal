# ADR-0012: Segredos em produção via AWS Secrets Manager

## Status

Aceita

## Contexto

Desde a Fase 1, o backend carrega toda a configuração — incluindo
segredos (`GITHUB_OAUTH_CLIENT_SECRET`, `GITHUB_APP_PRIVATE_KEY`,
`SESSION_SECRET`) — de variáveis de ambiente via `.env`
(`backend/src/config.py`). Isso é adequado para desenvolvimento local,
mas `docs/initial-architecture.md` (seção 14) exige que, em produção,
segredos fiquem no AWS Secrets Manager, nunca em `.env`. O template SAM
(`infra/sam/template.yaml`) já prevê um parâmetro
`SecretsManagerSecretArn` e concede à função Lambda permissão
`secretsmanager:GetSecretValue` sobre ele, mas nenhum código lê esse
segredo hoje — a Fase 4.1 fecha essa lacuna.

## Decisão

- Um único segredo JSON no AWS Secrets Manager, contendo exatamente os
  quatro valores sensíveis (`GITHUB_OAUTH_CLIENT_SECRET`,
  `GITHUB_APP_ID`, `GITHUB_APP_PRIVATE_KEY`, `SESSION_SECRET`) —
  não um segredo por valor. Uma única chamada `GetSecretValue` por
  cold start é mais simples, mais barata e já casa com o parâmetro
  único (`SecretsManagerSecretArn`) que o template já expõe; a escala
  do projeto não exige rotação independente por valor.
- `get_settings()` (`backend/src/config.py`) passa a checar uma
  variável de ambiente indicando o ARN do segredo; se presente, busca o
  segredo uma única vez (cacheado pelo `lru_cache` já existente),
  decodifica o JSON e injeta os valores antes de construir `Settings`.
  Se ausente (desenvolvimento local), o comportamento atual (`.env`,
  valores padrão) continua exatamente igual.
- Falha ao buscar o segredo, quando o ARN está configurado, é um erro
  fatal de inicialização — nunca um retorno silencioso aos valores
  padrão inseguros (`session_secret: "dev-only-insecure-secret"` etc.).

## Consequências

- Nenhum recurso AWS real é criado por esta decisão — criar e povoar o
  segredo em uma conta AWS real continua sendo um passo operacional
  separado e explícito, na mesma postura de todo o `infra/` até aqui.
- Desenvolvimento local não muda em nada: `.env` continua funcionando
  sem qualquer variável nova.
- A normalização de `GITHUB_APP_PRIVATE_KEY` (aceitar `\n` literal,
  ver `config.py`) continua se aplicando da mesma forma,
  independentemente da origem do valor (variável de ambiente ou
  Secrets Manager).
- `boto3` passa a ser dependência do backend, usada apenas neste
  caminho — sem impacto nos testes existentes, que não configuram a
  variável do ARN.

## Referências

- [docs/initial-architecture.md](../initial-architecture.md) — seção 14
  (segredos) e seção 17 (infraestrutura).
- [ADR-0005](0005-backend-lambda-api-gateway.md) — já listava o Secrets
  Manager como serviço inicial.
- [docs/phase-4.1-plan.md](../phase-4.1-plan.md).
