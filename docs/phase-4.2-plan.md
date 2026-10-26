# Plano da Fase 4.2 — Observabilidade (CloudWatch)

Sub-fase de [docs/phase-4-plan.md](phase-4-plan.md). Desdobramento da
[issue #13](https://github.com/cte-zl-ifrn/ifrn-editorial-portal/issues/13).

## Objetivo

Estender o logging estruturado já existente
(`backend/src/logging.py`, desde a Fase 1) com um registro de acesso
por requisição (rota, status, duração, `correlation_id`) e definir, no
template SAM, alarmes básicos do CloudWatch — sem introduzir nenhuma
decisão de arquitetura nova (a escolha de CloudWatch já é da
[ADR-0005](decisions/0005-backend-lambda-api-gateway.md)).

## Escopo

### Dentro

- Backend: middleware que loga, ao final de cada requisição, uma linha
  estruturada com método, rota, status HTTP, duração em milissegundos
  e `correlation_id` (o `correlation_id` já existe; falta o registro
  de acesso em si).
- Backend: contadores simples (ex.: total de requisições por rota,
  total de erros 4xx/5xx, total de submissões concluídas) — via
  métricas em formato EMF (Embedded Metric Format) no próprio log
  estruturado, sem exigir um serviço adicional além do CloudWatch já
  decidido.
- Infra: `infra/sam/template.yaml` — pelo menos dois alarmes do
  CloudWatch: taxa de erro da função Lambda e duração (latência)
  acima de um limite; ambos definidos como recurso do template
  (`AWS::CloudWatch::Alarm`), não implantados nesta fase.
- Revisão de `_SENSITIVE_KEYS` (`backend/src/logging.py`) à luz dos
  novos campos de log (rota pode conter parâmetros sensíveis? — não,
  os únicos parâmetros de rota hoje são identificadores públicos).

### Fora

- Métricas de negócio mais sofisticadas (ex.: funil de conversão de
  edição→PR) — fora do escopo de operação básica desta fase.
- X-Ray ou rastreamento distribuído — listado como "futuro, somente se
  necessário" (`docs/initial-architecture.md`, seção 17).
- Dashboards do CloudWatch — os alarmes bastam para o MVP; um
  dashboard pode ser adicionado depois, sem exigir nova decisão de
  arquitetura.
- Qualquer alerta ativo (SNS, e-mail) — os alarmes são definidos no
  template, mas conectar um canal de notificação real depende de uma
  implantação real (fora do escopo, ver `docs/phase-4-plan.md`).

## Entregáveis

1. `backend/src/app.py` (ou middleware dedicado): registro de acesso
   estruturado por requisição.
2. `backend/src/logging.py`: suporte a métricas EMF, se necessário.
3. `infra/sam/template.yaml`: dois `AWS::CloudWatch::Alarm` (taxa de
   erro, latência).
4. Testes cobrindo o middleware de registro de acesso (status, duração
   presentes; nenhum dado sensível).
5. `backend/README.md` e `infra/sam/README.md` atualizados.

**Entregue** (nomes reais): `backend/src/app.py` —
`correlation_id_middleware` renomeado para `access_log_middleware`,
agora com `try/finally` (loga mesmo em exceção não tratada), emitindo
`request.completed` (método, rota, status, duração,
`correlation_id`) e as métricas `RequestCount`/`ErrorCount`;
`backend/src/logging.py:log_metric` (emissor EMF genérico, escreve
direto em `stdout`); `backend/src/handlers/submissions.py` (métrica
`SubmissionCompleted` após sucesso); `backend/tests/test_observability.py`
(7 testes novos); `infra/sam/template.yaml`
(`FunctionErrorRateAlarm`, `FunctionLatencyAlarm`); `backend/README.md`
e `infra/sam/README.md` atualizados.

## Critérios de aceite / definição de pronto

- [x] Toda requisição produz uma linha de log estruturada com rota,
      status, duração e `correlation_id`
      (`test_every_request_produces_a_completed_access_log_line`,
      `test_access_log_covers_errors_too` — inclusive para rotas
      inexistentes/erros).
- [x] Nenhum dado sensível (segredo, cookie, token, conteúdo de
      documento) aparece nesse registro — comprovado estruturalmente:
      só quatro campos fixos são logados, nunca dados arbitrários da
      requisição
      (`test_access_log_never_includes_extra_fields_beyond_the_safe_set`).
- [x] `infra/sam/template.yaml` define ao menos os dois alarmes
      descritos acima; validado estruturalmente (mesma ressalva da Fase
      4.1 — AWS SAM CLI não disponível neste ambiente de
      desenvolvimento; recomendo `sam validate` de verdade antes de
      qualquer implantação real).
- [x] `ruff check` e `pytest` passam; nenhuma regressão — 73 testes no
      total no backend (66 + 7 novos).

## Riscos técnicos e decisões de arquitetura

Nenhuma ADR nova — esta sub-fase estende a
[ADR-0005](decisions/0005-backend-lambda-api-gateway.md), que já
definia CloudWatch como o backend de observabilidade do projeto.

- **Volume de log**: um registro de acesso por requisição é barato no
  volume esperado do MVP; se isso mudar, agregação/amostragem fica
  para uma fase futura.
- **Alarmes sem canal de notificação**: definir o alarme no template
  sem um destino real (SNS/e-mail) é intencional nesta fase — conectar
  um canal real depende de decidir quem deve ser notificado,
  responsabilidade institucional fora do escopo do código.

## Decisões tomadas durante a implementação

- **Alarmes usam as métricas nativas `AWS/Lambda`** (`Errors`,
  `Duration`, dimensionadas por `FunctionName`), não as métricas
  customizadas EMF (`RequestCount`/`ErrorCount`) — mais simples (sem
  precisar de um filtro de métrica sobre um namespace customizado) e
  já é exatamente o que o plano original pedia ("taxa de erro **da
  função Lambda**"). As métricas EMF continuam existindo, para consulta
  manual e dashboards futuros, mas não alimentam os alarmes desta fase.
- **`_SENSITIVE_KEYS` (`backend/src/logging.py`) não precisou de
  nenhuma alteração**: os novos campos logados (`method`, `path`,
  `status_code`, `duration_ms`) não são sensíveis, e a rota nunca
  carrega parâmetros hoje (nenhum handler tem path parameter — só rotas
  estáticas), então não há risco de um valor sensível aparecer dentro
  de `path`.
- O middleware existente (`correlation_id_middleware`) foi renomeado
  para `access_log_middleware`, já que passou a ser o dono do registro
  de acesso, não só do `correlation_id` — reflete melhor sua
  responsabilidade atual.
- O registro de acesso usa `try/finally` (não só um log no início e
  outro no fim) para garantir que uma exceção não tratada por nenhum
  `exception_handler` ainda produza a linha `request.completed` (com
  status 500 e a duração até a falha) — sem isso, o cenário mais
  importante de se observar (um bug real) seria justamente o que não
  aparece no log de acesso.

## Roteiro de validação manual (Fase 4.2.5)

- [x] Rodar o backend localmente, fazer algumas requisições, e
      confirmar visualmente que o log estruturado inclui rota, status
      e duração. Confirmado diretamente (via `TestClient`, sem exigir
      credenciais reais — `GET /health`):
      ```json
      {"level": "INFO", "logger": "src.app", "message": "request.completed", "correlation_id": "46e4d61a...", "method": "GET", "path": "/health", "status_code": 200, "duration_ms": 8.25}
      {"_aws": {...}, "Route": "/health", "RequestCount": 1}
      ```
- [x] Provocar um erro (ex.: rota inexistente) e confirmar que o
      registro de acesso também cobre esse caso. Confirmado (`GET
      /rota-que-nao-existe` → 404):
      ```json
      {"level": "INFO", "logger": "src.app", "message": "request.completed", ..., "status_code": 404, "duration_ms": 9.41}
      {"_aws": {...}, "Route": "/rota-que-nao-existe", "StatusCode": "404", "ErrorCount": 1}
      ```
- [x] `sam validate --template infra/sam/template.yaml` com os novos
      alarmes — mesma ressalva da Fase 4.1: AWS SAM CLI não disponível
      neste ambiente; validado estruturalmente com um parser YAML que
      reconhece as tags curtas do CloudFormation. Recomendo `sam
      validate` de verdade antes de qualquer implantação real.

## Dependências

- Nenhuma dependência de código de outras sub-fases — pode ser
  implementada isoladamente. Recomendada depois da Fase 4.1 (segredos)
  só pela ordem lógica do roadmap, não por dependência técnica.
