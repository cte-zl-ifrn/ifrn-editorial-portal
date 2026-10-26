import { describe, expect, it } from 'vitest'
import { markdownToTiptap } from '../src/lib/markdownToTiptap'
import { tiptapToMarkdown } from '../src/lib/tiptapToMarkdown'
import {
  ACESSO_MOODLE_BODY,
  ABRIR_CHAMADO_SUAP_BODY,
  COMO_FAZER_CURSOS_BODY,
} from './fixtures/realDocuments'

/**
 * Round-trip: markdown → Tiptap → markdown → Tiptap deve produzir a
 * MESMA árvore Tiptap da primeira conversão (equivalência semântica),
 * mesmo que o texto Markdown de saída não seja byte-a-byte idêntico ao
 * original — normalizações cosmética documentadas e estáveis (ver
 * docs/phase-2.2-plan.md e o cabeçalho de tiptapToMarkdown.ts) são
 * aceitáveis; perda ou distorção de estrutura não é.
 */
function expectStableRoundTrip(markdown: string): void {
  const firstPass = markdownToTiptap(markdown)
  const serialized = tiptapToMarkdown(firstPass)
  const secondPass = markdownToTiptap(serialized)

  expect(secondPass).toEqual(firstPass)
}

describe('round-trip markdown → Tiptap → markdown (documentos reais)', () => {
  it('é estável para _docs/ambiente-virtual/acesso-moodle.md', () => {
    expectStableRoundTrip(ACESSO_MOODLE_BODY)
  })

  it('é estável para _docs/central-servicos/abrir-chamado-suap.md', () => {
    expectStableRoundTrip(ABRIR_CHAMADO_SUAP_BODY)
  })

  it('é estável para _docs/proitec/como-fazer-cursos.md', () => {
    expectStableRoundTrip(COMO_FAZER_CURSOS_BODY)
  })

  it('é estável para um documento sintético cobrindo todo o escopo mínimo de nós', () => {
    const markdown = [
      '# Título principal',
      '',
      'Parágrafo com **negrito**, *itálico*, `código` e um [link](https://exemplo.org "T").',
      '',
      '---',
      '',
      '- Item um',
      '  - Subitem aninhado',
      '- Item dois',
      '',
      '1. Primeiro',
      '2. Segundo',
      '',
      '![Texto alternativo](https://exemplo.org/x.png "Título")',
      '',
    ].join('\n')

    expectStableRoundTrip(markdown)
  })
})
