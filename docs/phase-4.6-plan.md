# Plano da Fase 4.6 — Runbook operacional e LGPD

Sub-fase de [docs/phase-4-plan.md](phase-4-plan.md). Desdobramento da
[issue #13](https://github.com/cte-zl-ifrn/ifrn-editorial-portal/issues/13).

## Objetivo

Documentar, em um único lugar, os procedimentos operacionais que hoje
só existem na memória de quem já resolveu cada problema (dois
incidentes reais já ocorreram e foram documentados de forma dispersa
na Fase 3.1.5) e formalizar o que a Fase 4 implica para LGPD, sem
substituir a análise jurídica institucional.

## Escopo

### Dentro

- Novo `docs/runbook.md`: como rotacionar cada segredo (OAuth client
  secret, chave privada da GitHub App, `SESSION_SECRET`), como
  reinstalar/reconfigurar a GitHub App em `central-ajuda`, como
  diagnosticar as falhas comuns já vistas na prática — incluindo os
  dois incidentes reais da Fase 3.1.5 (instalação errada da GitHub
  App; troca acidental de credenciais OAuth App ↔ GitHub App) como
  exemplos resolvidos, e como ler os alarmes/logs da Fase 4.2.
- `docs/project-context.md`: fechar a questão em aberto "política
  institucional de retenção de logs" com uma proposta concreta (não
  uma decisão jurídica definitiva) — período sugerido e justificativa
  técnica, deixando claro que a palavra final é institucional.
- Revisão de `SECURITY.md` à luz de tudo que a Fase 4 adiciona
  (Secrets Manager, CSRF, rate limiting).

### Fora

- A análise jurídica formal de LGPD em si — continua sendo
  responsabilidade institucional, não do código ou da documentação
  técnica (já explícito na seção 15 do documento de arquitetura).
- Qualquer automação do procedimento de rotação de segredos — o
  runbook documenta o procedimento manual; automatizá-lo fica para uma
  fase futura, se necessário.

## Entregáveis

1. `docs/runbook.md` (novo).
2. `docs/project-context.md`: questão de retenção de logs fechada com
   uma proposta concreta.
3. `SECURITY.md` atualizado.

## Critérios de aceite / definição de pronto

- [ ] `docs/runbook.md` cobre, no mínimo: rotação de cada um dos
      quatro segredos, reinstalação/reconfiguração da GitHub App, e os
      dois incidentes reais da Fase 3.1.5 como exemplos resolvidos.
- [ ] `docs/project-context.md` não lista mais "política de retenção
      de logs" como questão totalmente em aberto — passa a ter uma
      proposta concreta registrada, com a ressalva de que a decisão
      institucional final ainda pode divergir.
- [ ] `SECURITY.md` reflete a superfície de segurança adicionada por
      toda a Fase 4.

## Riscos técnicos e decisões de arquitetura

Nenhuma ADR nova — esta sub-fase é inteiramente documentação, sem
decisão de arquitetura de código.

- **Runbook desatualizado com o tempo**: risco aceito, mitigado por
  manter o runbook próximo do código (`docs/`) e revisá-lo a cada
  incidente real futuro, como já aconteceu organicamente na Fase
  3.1.5.

## Roteiro de validação manual (Fase 4.6.5)

A ser executado e registrado quando a implementação estiver concluída:

- [ ] Revisão humana do `docs/runbook.md` — confirmar que os
      procedimentos descritos batem com a realidade do projeto (não
      são genéricos/copiados de um template).

## Dependências

- Recomendada por último, já que documenta operacionalmente as demais
  sub-fases (em especial a rotação de segredos da Fase 4.1 e os
  alarmes da Fase 4.2) — mas não tem dependência de código.
