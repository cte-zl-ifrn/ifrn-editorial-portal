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

## Critérios de aceite / definição de pronto

- [ ] Com a variável do ARN presente (mockada), `get_settings()`
      resolve os quatro valores sensíveis a partir do segredo, não do
      ambiente.
- [ ] Sem a variável do ARN, o comportamento é idêntico ao atual
      (nenhuma regressão nas fases anteriores).
- [ ] Falha ao buscar o segredo, com a variável presente, interrompe a
      inicialização com um erro claro — nunca um valor padrão
      inseguro em produção.
- [ ] Nenhum valor do segredo aparece em log, mesmo em caso de erro.
- [ ] `ruff check` e `pytest` passam; nenhuma regressão nos testes
      existentes.
- [ ] `sam validate --template infra/sam/template.yaml` continua
      válido com a nova variável de ambiente.

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

## Roteiro de validação manual (Fase 4.1.5)

A ser executado e registrado quando a implementação estiver concluída,
no mesmo formato das validações anteriores:

- [ ] Rodar o backend localmente sem a variável do ARN → comportamento
      idêntico ao atual.
- [ ] Rodar os testes automatizados com o segredo mockado → valores
      aplicados corretamente.
- [ ] Confirmar, por leitura de código (não por implantação real, que
      está fora do escopo), que nenhum caminho de erro loga o payload
      do segredo.

## Dependências

- Nenhuma dependência de código de outras sub-fases da Fase 4 — pode
  ser implementada isoladamente.
