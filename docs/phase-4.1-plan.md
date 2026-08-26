# Plano da Fase 4.1 — Segredos de produção via AWS Secrets Manager

Sub-fase de [docs/phase-4-plan.md](phase-4-plan.md). Desdobramento da
[issue #13](https://github.com/cte-zl-ifrn/ifrn-editorial-portal/issues/13).

## Objetivo

Permitir que o backend carregue `GITHUB_OAUTH_CLIENT_SECRET`,
`GITHUB_APP_ID`, `GITHUB_APP_PRIVATE_KEY` e `SESSION_SECRET` de um
segredo no AWS Secrets Manager quando implantado, sem alterar em nada
o desenvolvimento local (`.env` continua funcionando exatamente como
hoje).

## Escopo

### Dentro

- Backend: `get_settings()` (`backend/src/config.py`) passa a checar
  uma variável de ambiente (ex.: `SECRETS_MANAGER_SECRET_ARN`); se
  presente, busca o segredo uma única vez via `boto3`
  (`secretsmanager:GetSecretValue`), decodifica o JSON e injeta os
  valores antes de construir `Settings`.
- Backend: falha ao buscar o segredo (quando a variável está presente)
  interrompe a inicialização — nunca cai silenciosamente nos valores
  padrão inseguros.
- Backend: revisão de `_SENSITIVE_KEYS`
  (`backend/src/logging.py`) para garantir que nada relacionado a essa
  busca (ex.: o próprio ARN, que não é sensível, mas o payload do
  segredo, que é) apareça em log.
- Infra: `infra/sam/template.yaml` já concede
  `secretsmanager:GetSecretValue` sobre `SecretsManagerSecretArn` — só
  falta expor esse ARN como variável de ambiente da função (hoje o
  parâmetro existe, mas não é passado para `Environment.Variables`).
- Testes: sucesso (segredo mockado, valores aplicados), variável
  ausente (comportamento local inalterado), falha na busca (erro
  fatal, não fallback silencioso).
- Atualizar `backend/README.md` e `infra/sam/README.md`.

### Fora

- Criar ou popular o segredo em uma conta AWS real — ver a restrição
  registrada em [docs/phase-4-plan.md](phase-4-plan.md).
- Rotação automática de segredos — rotação continua sendo um
  procedimento manual, documentado na Fase 4.6 (runbook).
- Qualquer segredo além dos quatro já identificados hoje.

## Entregáveis

1. `backend/src/config.py`: carregamento condicional a partir do
   Secrets Manager, com fallback para `.env`/padrões quando a variável
   do ARN não está presente.
2. `backend/pyproject.toml`/`requirements*.txt`: `boto3` adicionado
   como dependência.
3. `infra/sam/template.yaml`: variável de ambiente com o ARN do
   segredo exposta à função Lambda.
4. Testes cobrindo os três cenários do escopo acima.
5. `docs/decisions/0012-segredos-secrets-manager.md` (ver
   [ADR-0012](decisions/0012-segredos-secrets-manager.md)).

**Entregue** (nomes reais): `backend/src/config.py` —
`SECRETS_MANAGER_SECRET_ARN_ENV_VAR`, `_SECRETS_MANAGER_KEY_MAP`,
`_load_secrets_manager_overrides()`, `get_settings()` estendido;
`backend/requirements.txt` e `backend/pyproject.toml` (`boto3`);
`infra/sam/template.yaml` (`SECRETS_MANAGER_SECRET_ARN` exposta em
`Globals.Function.Environment.Variables`); `backend/tests/test_config.py`
(4 testes novos); `backend/README.md` e `infra/sam/README.md`
atualizados.

## Critérios de aceite / definição de pronto

- [x] Com a variável do ARN presente (mockada), `get_settings()`
      resolve os quatro valores sensíveis a partir do segredo, não do
      ambiente
      (`test_get_settings_loads_overrides_from_secrets_manager_when_arn_is_present`).
- [x] Sem a variável do ARN, o comportamento é idêntico ao atual —
      nenhuma regressão nas fases anteriores
      (`test_get_settings_uses_env_when_secrets_manager_arn_is_absent`;
      os 62 testes das fases anteriores continuam passando).
- [x] Falha ao buscar o segredo, com a variável presente, interrompe a
      inicialização com um erro claro — nunca um valor padrão
      inseguro em produção (`test_get_settings_fails_loudly_when_secrets_manager_fetch_fails`,
      `test_get_settings_fails_loudly_when_secret_payload_is_missing_a_key`;
      `_load_secrets_manager_overrides` não captura nenhuma exceção).
- [x] Nenhum valor do segredo aparece em log — nenhum caminho do novo
      código faz log; `_SENSITIVE_KEYS` (`backend/src/logging.py`) já
      cobria os nomes relevantes e não precisou de alteração.
- [x] `ruff check` e `pytest` passam; nenhuma regressão nos testes
      existentes (66 testes no total no backend, 4 novos).
- [x] `sam validate --template infra/sam/template.yaml` continua
      válido com a nova variável de ambiente — validado estruturalmente
      via parser YAML com tags do CloudFormation (AWS SAM CLI não
      disponível neste ambiente de desenvolvimento).

## Riscos técnicos e decisões de arquitetura

Ver [ADR-0012](decisions/0012-segredos-secrets-manager.md) para a
decisão completa (um segredo único, busca uma vez por cold start,
falha fatal em vez de fallback silencioso).

- **Cold start mais lento**: uma chamada de rede adicional ao Secrets
  Manager no primeiro carregamento de cada instância Lambda — aceitável
  (cacheado pelo `lru_cache` já existente, uma vez por instância, não
  por requisição).
- **Custo**: `GetSecretValue` tem custo por chamada; com cache por
  instância, o volume é desprezível para o tráfego esperado do MVP.

## Decisões tomadas durante a implementação

- O ambiente de desenvolvimento deste worktree não tinha `pip` nem
  `boto3` instalados no `.venv` já existente — foi necessário
  `python -m ensurepip` antes de instalar as dependências. Não é uma
  decisão de arquitetura, só uma nota operacional para quem for
  reproduzir localmente.
- O AWS SAM CLI não está disponível neste ambiente — a validação do
  template foi feita por um parser YAML com constructor genérico para
  as tags curtas do CloudFormation (`!Ref`, `!If`, `!Sub`, `!GetAtt`,
  `!Equals`), suficiente para garantir que a estrutura do documento
  está correta, mas não substitui `sam validate` de verdade. Recomendo
  rodar `sam validate --template infra/sam/template.yaml` antes de
  qualquer implantação real.
- `_load_secrets_manager_overrides` propositalmente **não** captura
  nenhuma exceção (nem de rede, nem de parsing do JSON, nem de chave
  ausente no payload) — qualquer falha sobe direto e interrompe
  `create_app()` na importação do módulo (`backend/src/app.py`), que já
  falha imediatamente hoje. Reaproveita esse comportamento existente em
  vez de introduzir um novo.

## Roteiro de validação manual (Fase 4.1.5)

- [x] Rodar o backend localmente sem a variável do ARN → comportamento
      idêntico ao atual. Confirmado diretamente:
      `get_settings()` sem `SECRETS_MANAGER_SECRET_ARN` retorna
      `session_secret` a partir do valor padrão de sempre
      (`dev-only-insecure-secret...`), sem tocar `boto3`.
- [x] Rodar os testes automatizados com o segredo mockado → valores
      aplicados corretamente. Confirmado via `pytest` (4 testes novos em
      `test_config.py`) e também manualmente fora dos testes, com um
      `boto3.client` mockado retornando um segredo JSON completo —
      `session_secret` refletiu o valor do segredo, não do ambiente.
- [x] Confirmar, por leitura de código, que nenhum caminho de erro loga
      o payload do segredo — `_load_secrets_manager_overrides` não
      contém nenhuma chamada de log; qualquer falha sobe como exceção
      não tratada.
- [ ] **Pendente do mantenedor** (fora do que pode ser verificado sem
      credenciais reais): revisar a variável
      `SECRETS_MANAGER_SECRET_ARN` exposta em
      `infra/sam/template.yaml` e, quando decidir avançar para uma
      implantação real, confirmar com `sam validate`/`sam deploy` de
      verdade — fora do escopo desta fase (ver
      [docs/phase-4-plan.md](phase-4-plan.md)).

## Dependências

- Nenhuma dependência de código de outras sub-fases da Fase 4 — pode
  ser implementada isoladamente.
