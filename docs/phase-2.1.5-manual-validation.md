# Fase 2.1.5 — Validação manual

Conclusão operacional da validação manual da Fase 2.1
([docs/phase-2.1-plan.md](phase-2.1-plan.md)): carregamento do documento
com front matter separado do corpo e renderização somente leitura no
Tiptap, testado localmente contra o backend e o frontend reais.

Data: 2026-08-25

## Resultados

- [x] Login com usuário autorizado → documento carregado e renderizado no
      Tiptap, comparado visualmente com o Markdown original (título,
      parágrafos, negrito, lista numerada, divisor).
- [x] Painel de metadados exibe corretamente os campos do front matter do
      documento real (`layout`, `title`, `parent`, `categories`,
      `description`).
- [x] Login com usuário sem permissão → acesso negado (tela de não
      autorizado), sem vazamento de conteúdo do documento.
- [x] Tentativa de editar o conteúdo no Tiptap (clique e digitação)
      confirma que o editor está em modo somente leitura — nenhuma
      alteração é possível.
- [x] Inspeção da aba de rede confirma que `front_matter_raw` bate
      exatamente com o início do arquivo original no GitHub.

## Observações

- Testado com o documento de demonstração
  `_docs/ambiente-virtual/acesso-moodle.md` (mantido via override em
  `SAMPLE_DOCUMENT_PATH` no `.env` local, herdado da Fase 1/1.5) — não o
  novo padrão `_docs/proitec/como-fazer-cursos.md`. Cobre parágrafo,
  negrito, título, lista numerada e divisor; não exercita lista com
  marcadores, itálico ou imagem nesta rodada de validação manual — esses
  nós permanecem cobertos apenas pelos testes automatizados
  (`frontend/tests/markdownToTiptap.spec.ts` e
  `markdownToTiptap.realDocument.spec.ts`, este último já rodando contra o
  corpo real de `como-fazer-cursos.md`).
- O bloco `<blockquote class="dica">...</blockquote>` do documento
  apareceu como texto literal na tela, como esperado — HTML embutido
  nunca é interpretado como marcação (`html: false` no `markdown-it`, ver
  [ADR-0009](decisions/0009-conversao-markdown-tiptap-e-front-matter.md)).
  Comportamento intencional de segurança, não uma falha; transformar esse
  padrão em um nó de "bloco de aviso" estilizado fica para uma fase
  futura (fora da whitelist mínima da Fase 2.1).

## Efeito nos critérios de aceite da Fase 2.1

Todos os itens do roteiro de validação manual definido em
[docs/phase-2.1-plan.md](phase-2.1-plan.md#roteiro-de-validação-manual-fase-215)
foram confirmados. A Fase 2.1 está concluída e validada, tanto
automaticamente (31 testes de backend, 38 de frontend) quanto
manualmente. Pendente: validar visualmente lista com marcadores, itálico
e imagem em uma futura sessão manual, quando o `SAMPLE_DOCUMENT_PATH`
local for atualizado para `_docs/proitec/como-fazer-cursos.md` (ou outro
documento real que os contenha) — não bloqueia o início da Fase 2.2.
