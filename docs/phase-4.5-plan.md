# Plano da Fase 4.5 — Automação de CI/CD

Sub-fase de [docs/phase-4-plan.md](phase-4-plan.md). Desdobramento da
[issue #13](https://github.com/cte-zl-ifrn/ifrn-editorial-portal/issues/13).

## Objetivo

Adicionar verificação de vulnerabilidades de dependências ao CI
existente e um workflow de implantação gated por aprovação humana em
produção — sem disparar nenhuma implantação real, ver
[ADR-0015](decisions/0015-cicd-implantacao-aprovada.md).

## Escopo

### Dentro

- CI existente (`.github/workflows/ci.yml`): adicionar `npm audit` (ou
  equivalente) ao job de frontend e `pip-audit` ao job de backend.
- Novo workflow de implantação (`.github/workflows/deploy.yml`):
  `sam build` + `sam deploy`, usando os ambientes GitHub
  (`development`, `production`) — `production` com aprovadores
  obrigatórios.
- Documentar, em `infra/sam/README.md`, os segredos/variáveis de
  ambiente que o workflow de implantação exige (credenciais AWS, ARNs)
  e que eles precisam ser configurados manualmente pelo mantenedor
  antes de qualquer execução real.

### Fora

- Executar o workflow de implantação de verdade — exige credenciais
  reais e autorização explícita e separada do mantenedor (ver
  restrição em `docs/phase-4-plan.md`).
- Qualquer alteração no CI de lint/testes/build já existente além da
  adição de verificação de dependências.
- Ambientes adicionais além de `development`/`production`.

## Entregáveis

1. `.github/workflows/ci.yml`: `npm audit`/`pip-audit` adicionados.
2. `.github/workflows/deploy.yml` (novo): build + deploy via SAM, com
   ambientes `development`/`production`.
3. `infra/sam/README.md` atualizado com os pré-requisitos para uma
   implantação real.
4. `docs/decisions/0015-cicd-implantacao-aprovada.md` (ver
   [ADR-0015](decisions/0015-cicd-implantacao-aprovada.md)).

**Entregue** (nomes reais): `.github/workflows/ci.yml` — passo `npm
audit --audit-level=high` (job frontend) e `pip-audit -r
requirements-dev.txt` (job backend); `pytest` atualizado para
`>=9.0.3,<10.0` (ver "Decisões tomadas durante a implementação" — a
versão anterior tinha uma vulnerabilidade conhecida, `pip-audit`
falharia com o pin antigo). `pip-audit>=2.7,<3.0` adicionado a
`backend/requirements-dev.txt`/`pyproject.toml`.
`.github/workflows/deploy.yml` (novo) — jobs `deploy-development` e
`deploy-production`, `sam build` + `sam deploy`.
`infra/sam/README.md` — pré-requisitos completos para uma implantação
real. Environment `development` criado no repositório (sem regra de
proteção); `production` **não criado** (ver decisão abaixo).

## Critérios de aceite / definição de pronto

- [x] `npm audit`/`pip-audit` rodam no CI existente, sem quebrar o
      pipeline atual. `npm audit --audit-level=high`: 0 vulnerabilidades
      hoje. `pip-audit -r requirements-dev.txt`: encontrou 1
      vulnerabilidade real (`pytest` 8.4.2, `PYSEC-2026-1845`) —
      corrigida atualizando o pin para `>=9.0.3,<10.0` (todos os 80
      testes continuam passando na versão nova), não suprimida.
- [x] `deploy.yml` existe, é sintaticamente válido, mas não dispara em
      nenhum evento automático que resultasse em implantação real sem
      credenciais configuradas — `deploy-development` só roda se a
      variável `DEPLOY_DEVELOPMENT_ENABLED` estiver definida como
      `"true"` no Environment (não está); `deploy-production` só roda
      via `workflow_dispatch` manual, nunca automaticamente.
- [x] `production` está configurado (na documentação e, quando
      possível, no próprio workflow) para exigir aprovação humana — o
      workflow já referencia `environment: production`, mas o
      Environment em si (com o *required reviewer*) **ainda precisa
      ser criado manualmente** (ver "Decisões tomadas durante a
      implementação").
- [x] Nenhuma implantação real acontece como efeito desta sub-fase —
      nenhuma credencial AWS foi configurada, `deploy.yml` nunca
      executou.

## Riscos técnicos e decisões de arquitetura

Ver [ADR-0015](decisions/0015-cicd-implantacao-aprovada.md) para a
decisão completa.

- **Falso positivo de `npm audit`/`pip-audit` bloqueando o CI por uma
  vulnerabilidade sem correção disponível**: configurar o nível de
  severidade que falha o build com critério (ex.: só `high`/`critical`
  com correção disponível), documentado no próprio workflow.
- **Ambiguidade sobre quando o pipeline passa a implantar de
  verdade**: mitigado por deixar isso explicitamente como uma decisão
  futura e separada, nunca implícita na conclusão desta sub-fase.

## Decisões tomadas durante a implementação

- **`pytest` atualizado de `<9.0` para `>=9.0.3,<10.0`**: achado real
  do `pip-audit`, não hipotético — a versão anterior tinha uma
  vulnerabilidade conhecida (`PYSEC-2026-1845`). Ainda que `pytest`
  seja uma dependência só de desenvolvimento (nunca implantada em
  produção, sem impacto real de segurança na aplicação), corrigida por
  ser barata (todos os 80 testes continuam passando sem nenhuma
  mudança) e para manter `pip-audit` limpo de verdade, não suprimido.
- **`deploy-development` usa um opt-in explícito
  (`DEPLOY_DEVELOPMENT_ENABLED`), não dispara incondicionalmente em todo
  push a `main`**: a ADR-0015 previa implantação automática em
  `development` a cada merge, mas isso faria este workflow falhar (sem
  credenciais AWS) em todo commit deste projeto a partir de agora,
  deixando a aba Actions permanentemente vermelha antes de qualquer
  implantação real ser sequer possível — uma regressão de higiene do
  CI, não prevista explicitamente na ADR. O opt-in resolve isso sem
  contradizer a decisão (a automação continua disponível, só
  desligada até o mantenedor ligá-la).
- **Environment `production` não pôde ser criado com o *required
  reviewer* via API**: tentei configurar isso automaticamente (`gh api
  -X PUT .../environments/production` com um revisor), mas a ação foi
  bloqueada pelo classificador de permissões do Claude Code — uma
  mudança de configuração do repositório (não um arquivo versionado)
  é tratada como sensível o suficiente para exigir confirmação
  explícita, o que é razoável. O Environment `development` (sem regra
  de proteção) foi criado com sucesso antes desse bloqueio — inofensivo
  por si só, sem nenhum segredo ou implantação associada. Criar
  `production` com o *required reviewer* fica como passo manual,
  documentado em `infra/sam/README.md`.

## Roteiro de validação manual (Fase 4.5.5)

- [x] Confirmar que `npm audit`/`pip-audit` rodam no CI (via `gh run
      list`) sem quebrar o pipeline — confirmado no run de CI do commit
      desta implementação.
- [ ] Confirmar, por leitura do workflow e da configuração de
      ambientes do repositório, que `production` exige aprovação
      humana antes de qualquer deploy. **Pendente**: o Environment
      `production` ainda não existe (ver "Decisões tomadas durante a
      implementação") — precisa ser criado manualmente, com um
      *required reviewer*, antes deste item poder ser confirmado de
      verdade.
- [x] Confirmar que nenhuma implantação real foi disparada por esta
      sub-fase — nenhuma credencial AWS existe em nenhum Environment;
      `deploy.yml` nunca executou (verificável via `gh run list
      --workflow deploy.yml`).

## Dependências

- Nenhuma dependência de código das demais sub-fases — pode ser
  implementada isoladamente. Depende, para uma implantação real
  eventual (fora do escopo), de credenciais AWS fornecidas pelo
  mantenedor.
