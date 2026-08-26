# Plano da Fase 3 — Escrita via branch e Pull Request

Desdobramento da [issue #12](https://github.com/cte-zl-ifrn/ifrn-editorial-portal/issues/12).

## Objetivo

Fechar o caminho crítico completo do portal: depois de ler (Fase 1),
renderizar e editar (Fase 2), a Fase 3 grava de fato a alteração no
`central-ajuda` — sempre por branch própria e Pull Request, nunca por
push direto na `main` (ADR-0006). É a primeira fase em que a GitHub App
usa permissões de escrita, já previstas desde
[ADR-0004](decisions/0004-integracao-github-app.md) mas mantidas em
somente leitura até aqui.

```text
corpo editado no Tiptap (Fase 2.2)
  → serializado para Markdown (frontend, já existe)
  → revalidação de conflito + front matter fresco (backend)
  → branch derivada de main
  → commit do arquivo alterado
  → Pull Request aberto contra main
```

## Por que dividir em sub-fases

Escrever um documento e escrever assets (imagens/arquivos) têm riscos e
testes bem diferentes: o primeiro é validar que o mecanismo de
branch+commit+PR funciona para um único arquivo de texto; o segundo
adiciona upload, validação de tipo/tamanho/assinatura de arquivo e
referências relativas no Markdown. Seguindo o mesmo padrão das fases
anteriores:

| Sub-fase | Resumo | Documento |
|---|---|---|
| **Fase 3.1** | Escrita de um único documento Markdown (sem assets): branch, commit, Pull Request | [docs/phase-3.1-plan.md](phase-3.1-plan.md) |
| **Fase 3.2** | Upload e commit de imagens/arquivos referenciados no documento, no mesmo branch/PR | [docs/phase-3.2-plan.md](phase-3.2-plan.md) |

## Decisão de arquitetura desta fase

[ADR-0011](decisions/0011-escrita-branch-commit-pull-request.md) fecha,
antes de dividir o trabalho:

1. gravação via chamadas sequenciais à Contents API (uma por arquivo),
   não a Git Data API de blobs/trees;
2. conflito de concorrência detectado revalidando o arquivo (via a
   própria Contents API) imediatamente antes de gravar;
3. front matter sempre lido de novo no momento da gravação, nunca
   confiado a partir do que o cliente enviou;
4. idempotência é best-effort nesta fase — sem armazenamento de
   deduplicação, coerente com o MVP sem banco de dados;
5. a Fase 3.1 escreve apenas no documento de demonstração fixo já usado
   nas fases anteriores — escolha de caminho e criação de novos
   documentos ficam para depois.

## Fora do escopo (toda a Fase 3)

- Listagem de múltiplos documentos ou criação de novo documento a partir
  de categoria/slug (seção 8.2 do documento de arquitetura).
- Aprovação editorial dentro do portal — revisão e merge continuam sendo
  feitos por humanos no `central-ajuda` (ADR-0006).
- Acompanhamento de status do Pull Request após a criação (ex.:
  `GET /api/submissions/{id}/status`) — a resposta síncrona da submissão
  já inclui o link do PR; polling de status fica para uma fase futura, se
  necessário.
- Idempotência real (deduplicação de submissões repetidas) — ver
  ADR-0011.
- Qualquer alteração no front matter pelo usuário — continua somente
  leitura.

## Riscos compartilhados entre 3.1 e 3.2

| Risco | Impacto | Mitigação |
|---|---|---|
| GitHub App com permissões de escrita usadas incorretamente (escrita fora do repositório/branch/caminho esperado) | Alto | `owner`/`repo`/`branch` base fixos no backend (RF-21, já validado nas fases anteriores); caminho do documento continua fixo na Fase 3.1 |
| Conflito de edição concorrente não detectado | Alto | Revalidação de `sha` imediatamente antes de gravar (ADR-0011), sem cache |
| Submissão duplicada por retry | Médio | Aceito como limitação nesta fase (ADR-0011); branch/PR duplicados são visíveis e podem ser fechados manualmente |
| PR criado com corpo/branch mal formatado, dificultando a revisão humana | Médio | Modelo de PR já especificado (seção 8.4 do documento de arquitetura), com testes de conteúdo do corpo do PR |
| Permissões de escrita da GitHub App configuradas mais amplas que o necessário | Alto | Tabela de permissões da ADR-0004 é o teto; nenhuma permissão além de `Contents` e `Pull requests` é solicitada |

## Definição de pronto da Fase 3

- Fase 3.1 e Fase 3.2 concluídas conforme seus próprios critérios de
  aceite;
- ambas validadas manualmente (Fase 3.1.5 / Fase 3.2.5), no mesmo formato
  das validações anteriores;
- pelo menos uma submissão real de teste contra o `central-ajuda`,
  explicitamente autorizada pelo mantenedor (ver
  [issue #12](https://github.com/cte-zl-ifrn/ifrn-editorial-portal/issues/12))
  — incluindo, na Fase 3.1.5, o merge real de um dos Pull Requests
  gerados, não apenas fechá-lo sem merge;
- `docs/api/openapi.yaml`, `docs/project-context.md` e `docs/glossary.md`
  atualizados.

Critérios detalhados por sub-fase estão em
[docs/phase-3.1-plan.md](phase-3.1-plan.md) e
[docs/phase-3.2-plan.md](phase-3.2-plan.md).
