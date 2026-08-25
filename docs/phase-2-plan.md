# Plano da Fase 2 — Caminho crítico de edição

Desdobramento da [issue #11](https://github.com/cte-zl-ifrn/ifrn-editorial-portal/issues/11).

## Objetivo

Avançar do caminho crítico de **leitura** (Fase 1/1.5 — ver
[docs/phase-1-plan.md](phase-1-plan.md) e
[docs/phase-1.5-manual-validation.md](phase-1.5-manual-validation.md)) para
o caminho crítico de **edição**: carregar um documento real do
`central-ajuda` no editor Tiptap, permitir a edição do corpo do texto e
serializar o resultado de volta para Markdown com front matter, fiel ao
formato original.

```text
documento Markdown (GitHub App, leitura)
  → separação front matter / corpo (backend)
  → corpo em Markdown → documento Tiptap (frontend)     [Fase 2.1]
  → edição no Tiptap (frontend)                          [Fase 2.2]
  → documento Tiptap → corpo em Markdown (frontend)      [Fase 2.2]
  → front matter original + corpo serializado             [Fase 2.2]
```

A Fase 2 **não grava nada no `central-ajuda`**. Não há branch, commit ou
Pull Request nesta fase — isso é Fase 3, conforme já delimitado em
`docs/initial-architecture.md` (seção 3, "Fora do MVP" não se aplica mais
integralmente, mas a ordem de implementação por fases continua a mesma:
leitura → edição → submissão).

## Por que dividir em sub-fases

Acoplar "ler e renderizar" com "editar e serializar" no mesmo incremento
tornaria difícil isolar falhas: um bug de renderização (parser Markdown →
Tiptap) e um bug de serialização (Tiptap → Markdown) têm causas, testes e
critérios de aceite completamente diferentes. Seguindo o padrão que
funcionou na Fase 1 → Fase 1.5 (implementação automatizada, depois
validação manual dedicada), a Fase 2 é dividida em:

| Sub-fase | Resumo | Documento |
|---|---|---|
| **Fase 2.1** | Carregar um documento real, separar front matter do corpo, renderizar o corpo no Tiptap em modo **somente leitura** | [docs/phase-2.1-plan.md](phase-2.1-plan.md) |
| **Fase 2.2** | Habilitar edição no Tiptap e serializar o corpo editado de volta para Markdown, recombinando com o front matter original | [docs/phase-2.2-plan.md](phase-2.2-plan.md) |

Cada sub-fase é testável isoladamente e tem seu próprio roteiro de
validação manual, a ser registrado como Fase 2.1.5 / Fase 2.2.5 (mesmo
padrão da Fase 1.5) quando concluído.

## Decisão de arquitetura desta fase

[ADR-0009](decisions/0009-conversao-markdown-tiptap-e-front-matter.md)
fecha três pontos antes de dividir o trabalho:

1. o front matter é preservado como **texto bruto** (não é editado nem
   reserializado nesta fase) — elimina o risco de diff cosmético de YAML;
2. a separação front matter/corpo acontece no **backend**;
3. o parsing Markdown → Tiptap usa uma biblioteca de tokens (parser
   controlado, restrito ao whitelist da ADR-0002); a serialização Tiptap →
   Markdown é um **serializer próprio**, não delegado a uma lib genérica.

## Fora do escopo (toda a Fase 2)

- Qualquer escrita no `central-ajuda`: branch, commit, Pull Request (Fase 3).
- Upload de imagens ou arquivos (Fase 3, ver ADR-0007).
- Edição dos campos do front matter (título, categoria, tags etc.) — o
  front matter é preservado verbatim, não editado.
- Listagem geral de documentos / criação de novo documento — a Fase 2
  continua operando sobre o documento de demonstração fixo já usado na
  Fase 1 (`_docs/ambiente-virtual/acesso-moodle.md`), ou outro documento
  único definido durante a Fase 2.1.
- Validação de links, acessibilidade de imagens ou outras validações de
  conteúdo além da fidelidade da conversão Markdown ↔ Tiptap.
- Persistência de rascunhos entre sessões.

## Riscos compartilhados entre 2.1 e 2.2

| Risco | Impacto | Mitigação |
|---|---|---|
| Conversão com perda ou distorção de formatação | Alto | Parser restrito ao whitelist da ADR-0002; testes de round-trip com fixtures reais do `central-ajuda` |
| Front matter divergente após reconstrução | Alto | Preservado como texto bruto (ADR-0009), nunca reserializado |
| Escopo de nós Markdown maior do que o Tiptap suporta hoje (tabelas, blocos de aviso, passos numerados) | Médio | Escopo de nós suportados definido explicitamente em cada sub-fase; nós fora do escopo são tratados de forma previsível (ver ADR-0009), não descartados silenciosamente |
| Mudança de contrato da API de leitura de documento quebra testes/consumidores da Fase 1 | Baixo | Nenhum consumidor externo depende do formato antigo; testes e OpenAPI atualizados como parte da Fase 2.1 |

Ver também a tabela de riscos consolidada em
[docs/project-context.md](project-context.md#riscos-conhecidos).

## Definição de pronto da Fase 2

A Fase 2 é considerada concluída quando:

- Fase 2.1 e Fase 2.2 estiverem concluídas conforme seus próprios
  critérios de aceite;
- ambas tiverem sido validadas manualmente (Fase 2.1.5 / Fase 2.2.5),
  registradas no mesmo formato de
  [docs/phase-1.5-manual-validation.md](phase-1.5-manual-validation.md);
- `docs/api/openapi.yaml` refletir o contrato final de leitura/edição de
  documento;
- `docs/project-context.md` e `docs/glossary.md` estiverem atualizados com
  quaisquer termos ou decisões novas;
- nenhuma escrita real tiver ocorrido no `central-ajuda` em nenhum momento
  do processo.

Critérios detalhados por sub-fase estão em
[docs/phase-2.1-plan.md](phase-2.1-plan.md) e
[docs/phase-2.2-plan.md](phase-2.2-plan.md).
