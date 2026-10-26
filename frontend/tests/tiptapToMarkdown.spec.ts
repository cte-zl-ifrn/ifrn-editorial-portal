import { describe, expect, it } from 'vitest'
import { tiptapToMarkdown, UnsupportedNodeError } from '../src/lib/tiptapToMarkdown'
import type { TiptapDocument } from '../src/types/tiptap'

function doc(...content: TiptapDocument['content']): TiptapDocument {
  return { type: 'doc', content }
}

describe('tiptapToMarkdown', () => {
  it('serializes a paragraph', () => {
    const markdown = tiptapToMarkdown(
      doc({ type: 'paragraph', content: [{ type: 'text', text: 'Um parágrafo simples.' }] }),
    )
    expect(markdown).toBe('Um parágrafo simples.\n')
  })

  it('serializes headings of every level', () => {
    const markdown = tiptapToMarkdown(
      doc(
        { type: 'heading', attrs: { level: 1 }, content: [{ type: 'text', text: 'H1' }] },
        { type: 'heading', attrs: { level: 2 }, content: [{ type: 'text', text: 'H2' }] },
        { type: 'heading', attrs: { level: 3 }, content: [{ type: 'text', text: 'H3' }] },
      ),
    )
    expect(markdown).toBe('# H1\n\n## H2\n\n### H3\n')
  })

  it('serializes a bullet list', () => {
    const markdown = tiptapToMarkdown(
      doc({
        type: 'bulletList',
        content: [
          {
            type: 'listItem',
            content: [{ type: 'paragraph', content: [{ type: 'text', text: 'Um' }] }],
          },
          {
            type: 'listItem',
            content: [{ type: 'paragraph', content: [{ type: 'text', text: 'Dois' }] }],
          },
        ],
      }),
    )
    expect(markdown).toBe('- Um\n- Dois\n')
  })

  it('serializes an ordered list respecting a non-default start', () => {
    const markdown = tiptapToMarkdown(
      doc({
        type: 'orderedList',
        attrs: { start: 3 },
        content: [
          {
            type: 'listItem',
            content: [{ type: 'paragraph', content: [{ type: 'text', text: 'Terceiro' }] }],
          },
          {
            type: 'listItem',
            content: [{ type: 'paragraph', content: [{ type: 'text', text: 'Quarto' }] }],
          },
        ],
      }),
    )
    expect(markdown).toBe('3. Terceiro\n4. Quarto\n')
  })

  it('serializes bold, italic and combined marks with correct nesting', () => {
    const markdown = tiptapToMarkdown(
      doc({
        type: 'paragraph',
        content: [
          { type: 'text', text: 'Texto ' },
          { type: 'text', text: 'negrito', marks: [{ type: 'bold' }] },
          { type: 'text', text: ' e ' },
          { type: 'text', text: 'itálico', marks: [{ type: 'italic' }] },
          { type: 'text', text: ' e ' },
          { type: 'text', text: 'ambos', marks: [{ type: 'bold' }, { type: 'italic' }] },
          { type: 'text', text: '.' },
        ],
      }),
    )
    expect(markdown).toBe('Texto **negrito** e *itálico* e ***ambos***.\n')
  })

  it('serializes a link, with and without title', () => {
    const markdown = tiptapToMarkdown(
      doc({
        type: 'paragraph',
        content: [
          {
            type: 'text',
            text: 'o portal',
            marks: [{ type: 'link', attrs: { href: 'https://exemplo.org', title: 'título' } }],
          },
          { type: 'text', text: ' e ' },
          {
            type: 'text',
            text: 'outro',
            marks: [{ type: 'link', attrs: { href: 'https://x.org' } }],
          },
        ],
      }),
    )
    expect(markdown).toBe('[o portal](https://exemplo.org "título") e [outro](https://x.org)\n')
  })

  it('serializes a standalone image node', () => {
    const markdown = tiptapToMarkdown(
      doc({
        type: 'image',
        attrs: { src: 'https://exemplo.org/foto.png', alt: 'Texto alternativo', title: 'Título' },
      }),
    )
    expect(markdown).toBe('![Texto alternativo](https://exemplo.org/foto.png "Título")\n')
  })

  it('serializes inline code using the code mark, without escaping its content', () => {
    const markdown = tiptapToMarkdown(
      doc({
        type: 'paragraph',
        content: [
          { type: 'text', text: 'Rode ' },
          { type: 'text', text: 'a*b_c', marks: [{ type: 'code' }] },
          { type: 'text', text: '.' },
        ],
      }),
    )
    expect(markdown).toBe('Rode `a*b_c`.\n')
  })

  it('serializes a horizontal rule', () => {
    const markdown = tiptapToMarkdown(
      doc(
        { type: 'paragraph', content: [{ type: 'text', text: 'Antes' }] },
        { type: 'horizontalRule' },
        { type: 'paragraph', content: [{ type: 'text', text: 'Depois' }] },
      ),
    )
    expect(markdown).toBe('Antes\n\n---\n\nDepois\n')
  })

  it('serializes a hard break as a backslash + newline', () => {
    const markdown = tiptapToMarkdown(
      doc({
        type: 'paragraph',
        content: [
          { type: 'text', text: 'Linha 1' },
          { type: 'hardBreak' },
          { type: 'text', text: 'Linha 2' },
        ],
      }),
    )
    expect(markdown).toBe('Linha 1\\\nLinha 2\n')
  })

  it('serializes nested lists with indentation', () => {
    const markdown = tiptapToMarkdown(
      doc({
        type: 'bulletList',
        content: [
          {
            type: 'listItem',
            content: [
              { type: 'paragraph', content: [{ type: 'text', text: 'Item' }] },
              {
                type: 'bulletList',
                content: [
                  {
                    type: 'listItem',
                    content: [{ type: 'paragraph', content: [{ type: 'text', text: 'Subitem' }] }],
                  },
                ],
              },
            ],
          },
        ],
      }),
    )
    expect(markdown).toBe('- Item\n  - Subitem\n')
  })

  it('escapes literal markdown-significant characters in plain text', () => {
    const markdown = tiptapToMarkdown(
      doc({
        type: 'paragraph',
        content: [{ type: 'text', text: 'Full HD (1920*1080) e _sublinhado_ literal' }],
      }),
    )
    expect(markdown).toBe('Full HD (1920\\*1080) e \\_sublinhado\\_ literal\n')
  })

  it('does not escape square brackets in plain text (checklist-style content)', () => {
    const markdown = tiptapToMarkdown(
      doc({ type: 'paragraph', content: [{ type: 'text', text: '[x] Tarefa concluída' }] }),
    )
    expect(markdown).toBe('[x] Tarefa concluída\n')
  })

  it('throws UnsupportedNodeError for an unknown node type', () => {
    expect(() => tiptapToMarkdown(doc({ type: 'blockquote', content: [] }))).toThrow(
      UnsupportedNodeError,
    )
  })

  it('returns an empty string for an empty document', () => {
    expect(tiptapToMarkdown({ type: 'doc', content: [] })).toBe('')
  })
})
