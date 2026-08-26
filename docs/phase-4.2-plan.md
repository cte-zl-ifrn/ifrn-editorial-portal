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

## Critérios de aceite / definição de pronto

- [ ] Toda requisição produz uma linha de log estruturada com rota,
      status, duração e `correlation_id`.
- [ ] Nenhum dado sensível (segredo, cookie, token, conteúdo de
      documento) aparece nesse registro — mesma garantia já validada
      para os logs existentes.
- [ ] `infra/sam/template.yaml` define ao menos os dois alarmes
      descritos acima; `sam validate` continua válido.
- [ ] `ruff check` e `pytest` passam; nenhuma regressão.

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

## Roteiro de validação manual (Fase 4.2.5)

A ser executado e registrado quando a implementação estiver concluída:

- [ ] Rodar o backend localmente, fazer algumas requisições, e
      confirmar visualmente que o log estruturado inclui rota, status
      e duração.
- [ ] Provocar um erro (ex.: rota inexistente) e confirmar que o
      registro de acesso também cobre esse caso.
- [ ] `sam validate --template infra/sam/template.yaml` com os novos
      alarmes.

## Dependências

- Nenhuma dependência de código de outras sub-fases — pode ser
  implementada isoladamente. Recomendada depois da Fase 4.1 (segredos)
  só pela ordem lógica do roadmap, não por dependência técnica.
