# Plano da Fase 4 — Segurança e operação

Desdobramento da [issue #13](https://github.com/cte-zl-ifrn/ifrn-editorial-portal/issues/13).

## Objetivo

Com o caminho crítico completo já funcionando (ler, editar e gravar via
branch+PR — Fases 1 a 3), a Fase 4 prepara o portal para operar com
segurança fora do laptop de desenvolvimento: segredos fora de `.env`,
observabilidade, proteção contra abuso, superfície HTTP endurecida,
pipeline de implantação e documentação operacional — conforme
`docs/initial-architecture.md`, seção 14 (segurança), 15 (LGPD), 16
(CI/CD) e 17 (infraestrutura).

## Por que dividir em sub-fases

Cada item do escopo da issue #13 é uma preocupação independente, com
riscos e forma de validação próprios — misturá-los tornaria qualquer
sub-fase difícil de revisar isoladamente. A divisão abaixo segue
exatamente os seis pontos da issue, na ordem de menor para maior
dependência entre eles (segredos antes de observabilidade, porque
logging não deve nunca vazar um segredo mal gerenciado; runbook por
último, porque documenta operacionalmente tudo que vier antes):

| Sub-fase | Resumo | Documento |
|---|---|---|
| **Fase 4.1** | Segredos de produção via AWS Secrets Manager | [docs/phase-4.1-plan.md](phase-4.1-plan.md) |
| **Fase 4.2** | Observabilidade: logs estruturados, métricas e alarmes no CloudWatch | [docs/phase-4.2-plan.md](phase-4.2-plan.md) |
| **Fase 4.3** | Rate limiting / proteção contra abuso | [docs/phase-4.3-plan.md](phase-4.3-plan.md) |
| **Fase 4.4** | Segurança da aplicação: cabeçalhos HTTP, CSRF cross-origin, validação de entrada, revisão de permissões | [docs/phase-4.4-plan.md](phase-4.4-plan.md) |
| **Fase 4.5** | Automação de CI/CD (build, testes, lint, implantação aprovada) | [docs/phase-4.5-plan.md](phase-4.5-plan.md) |
| **Fase 4.6** | Runbook operacional e LGPD | [docs/phase-4.6-plan.md](phase-4.6-plan.md) |

## Decisões de arquitetura desta fase

Quatro novas ADRs fecham, antes de dividir o trabalho, as decisões que
não eram óbvias a partir do que já existia:

- [ADR-0012](decisions/0012-segredos-secrets-manager.md) — um único
  segredo JSON no Secrets Manager, buscado uma vez por cold start.
- [ADR-0013](decisions/0013-rate-limiting-api-gateway.md) — throttling
  nativo do API Gateway, não um limitador de aplicação com estado
  compartilhado.
- [ADR-0014](decisions/0014-csrf-cookies-cross-origin.md) — cabeçalho
  customizado exigido em requisições de escrita, para cobrir o que
  `SameSite=None` deixa de proteger.
- [ADR-0015](decisions/0015-cicd-implantacao-aprovada.md) — implantação
  automática em `development`, aprovação humana obrigatória em
  `production`.

A Fase 4.2 (observabilidade) não introduz uma decisão de arquitetura
nova — apenas estende o que a [ADR-0005](decisions/0005-backend-lambda-api-gateway.md)
já havia decidido (CloudWatch como backend de observabilidade).

## Restrição que atravessa toda a fase: nenhuma implantação real ainda

Como em toda fase anterior, **nenhum recurso AWS real será criado**
como efeito colateral do código e dos templates desta fase. Segredos,
alarmes, throttling e o próprio pipeline de implantação continuam
sendo código e template revisáveis — validados localmente (testes com
mocks, `sam validate`) — até que o mantenedor forneça credenciais reais
e autorize explicitamente uma primeira implantação. Isso é
deliberado: mudanças de infraestrutura real são difíceis de reverter e
têm custo, então merecem uma decisão separada da aprovação desta
proposta de divisão.

## Fora do escopo (toda a Fase 4)

- A própria implantação real em uma conta AWS (ver restrição acima).
- WAF, X-Ray, DynamoDB ou qualquer serviço listado como "futuro,
  somente se necessário" em `docs/initial-architecture.md`, seção 17.
- Análise jurídica formal de LGPD — a Fase 4.6 documenta o necessário
  para uma análise institucional, mas não a substitui (seção 15 do
  documento de arquitetura já deixa isso explícito).
- Qualquer mudança de funcionalidade do produto (edição, submissão,
  assets) — esta fase é inteiramente sobre segurança e operação do que
  já existe.

## Riscos compartilhados entre as sub-fases

| Risco | Impacto | Mitigação |
|---|---|---|
| Segredo vazado em log, por um campo novo não coberto pelo filtro existente | Alto | `_SENSITIVE_KEYS` (`backend/src/logging.py`) revisado na Fase 4.1 e 4.2; nenhum segredo literal em template ou código |
| Configuração real de produção divergindo do que o template documenta | Médio | Templates (`infra/sam/`) permanecem a única fonte de verdade da infraestrutura-alvo; nenhuma configuração "só na AWS" sem refletir no repositório |
| Falso senso de segurança por documentar proteções que só valem depois de uma implantação real | Médio | Cada sub-fase deixa explícito, no próprio plano, o que já vale hoje (código, testes) versus o que só vale após implantação |
| Implantação real acontecendo sem autorização explícita | Alto | ADR-0015: pipeline existe mas não é disparado sem credenciais fornecidas e confirmação explícita do mantenedor |

## Definição de pronto da Fase 4

- As seis sub-fases concluídas conforme seus próprios critérios de
  aceite;
- todas validadas manualmente (Fase 4.X.5), no mesmo formato das
  validações anteriores — com a ressalva de que, onde a validação
  depende de infraestrutura real não implantada, isso fica
  explicitamente registrado como tal, não simulado;
- `docs/project-context.md` e `docs/decisions/README.md` atualizados;
- nenhuma implantação real ocorre sem autorização explícita e
  separada do mantenedor.

Critérios detalhados por sub-fase estão em
[docs/phase-4.1-plan.md](phase-4.1-plan.md) até
[docs/phase-4.6-plan.md](phase-4.6-plan.md).
