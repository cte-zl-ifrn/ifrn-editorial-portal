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

## Critérios de aceite / definição de pronto

- [ ] `npm audit`/`pip-audit` rodam no CI existente, sem quebrar o
      pipeline atual (nenhuma vulnerabilidade crítica conhecida hoje
      nas dependências atuais, a confirmar na implementação).
- [ ] `deploy.yml` existe, é sintaticamente válido, mas não dispara em
      nenhum evento automático que resultasse em implantação real sem
      credenciais configuradas.
- [ ] `production` está configurado (na documentação e, quando
      possível, no próprio workflow) para exigir aprovação humana.
- [ ] Nenhuma implantação real acontece como efeito desta sub-fase.

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

## Roteiro de validação manual (Fase 4.5.5)

A ser executado e registrado quando a implementação estiver concluída:

- [ ] Confirmar que `npm audit`/`pip-audit` rodam no CI (via `gh run
      list`) sem quebrar o pipeline.
- [ ] Confirmar, por leitura do workflow e da configuração de
      ambientes do repositório, que `production` exige aprovação
      humana antes de qualquer deploy.
- [ ] Confirmar que nenhuma implantação real foi disparada por esta
      sub-fase.

## Dependências

- Nenhuma dependência de código das demais sub-fases — pode ser
  implementada isoladamente. Depende, para uma implantação real
  eventual (fora do escopo), de credenciais AWS fornecidas pelo
  mantenedor.
