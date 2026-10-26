import { describe, expect, it } from 'vitest'
import { markdownToTiptap } from '../src/lib/markdownToTiptap'

describe('markdownToTiptap', () => {
  it('converts a paragraph', () => {
    const doc = markdownToTiptap('Um parágrafo simples.')
    expect(doc).toEqual({
      type: 'doc',
      content: [{ type: 'paragraph', content: [{ type: 'text', text: 'Um parágrafo simples.' }] }],
    })
  })

  it('converts headings of every level', () => {
    const doc = markdownToTiptap('# H1\n\n## H2\n\n### H3')
    expect(doc.content).toEqual([
      { type: 'heading', attrs: { level: 1 }, content: [{ type: 'text', text: 'H1' }] },
      { type: 'heading', attrs: { level: 2 }, content: [{ type: 'text', text: 'H2' }] },
      { type: 'heading', attrs: { level: 3 }, content: [{ type: 'text', text: 'H3' }] },
    ])
  })

  it('converts a bullet list', () => {
    const doc = markdownToTiptap('- Um\n- Dois\n')
    expect(doc.content).toEqual([
      {
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
      },
    ])
  })

  it('converts an ordered list, including a non-default start', () => {
    const doc = markdownToTiptap('3. Terceiro\n4. Quarto\n')
    expect(doc.content).toEqual([
      {
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
      },
    ])
  })

  it('omits the start attribute when the ordered list starts at 1', () => {
    const doc = markdownToTiptap('1. Primeiro\n')
    const orderedList = doc.content[0]
    expect(orderedList.attrs).toBeUndefined()
  })

  it('converts bold and italic as marks, including combined marks', () => {
    const doc = markdownToTiptap('Texto **negrito** e *itálico* e **_ambos_**.')
    const [paragraph] = doc.content
    expect(paragraph.content).toEqual([
      { type: 'text', text: 'Texto ' },
      { type: 'text', text: 'negrito', marks: [{ type: 'bold' }] },
      { type: 'text', text: ' e ' },
      { type: 'text', text: 'itálico', marks: [{ type: 'italic' }] },
      { type: 'text', text: ' e ' },
      { type: 'text', text: 'ambos', marks: [{ type: 'bold' }, { type: 'italic' }] },
      { type: 'text', text: '.' },
    ])
  })

  it('converts a link', () => {
    const doc = markdownToTiptap('Veja [o portal](https://exemplo.org "título").')
    const [paragraph] = doc.content
    expect(paragraph.content).toEqual([
      { type: 'text', text: 'Veja ' },
      {
        type: 'text',
        text: 'o portal',
        marks: [{ type: 'link', attrs: { href: 'https://exemplo.org', title: 'título' } }],
      },
      { type: 'text', text: '.' },
    ])
  })

  it('converts a standalone image paragraph into a block image node', () => {
    const doc = markdownToTiptap('![Texto alternativo](https://exemplo.org/foto.png "Um título")')
    expect(doc.content).toEqual([
      {
        type: 'image',
        attrs: { src: 'https://exemplo.org/foto.png', alt: 'Texto alternativo', title: 'Um título' },
      },
    ])
  })

  it('converts inline code using the code mark', () => {
    const doc = markdownToTiptap('Rode `npm test` para validar.')
    const [paragraph] = doc.content
    expect(paragraph.content).toEqual([
      { type: 'text', text: 'Rode ' },
      { type: 'text', text: 'npm test', marks: [{ type: 'code' }] },
      { type: 'text', text: ' para validar.' },
    ])
  })

  it('converts a horizontal rule', () => {
    const doc = markdownToTiptap('Antes\n\n---\n\nDepois')
    expect(doc.content).toEqual([
      { type: 'paragraph', content: [{ type: 'text', text: 'Antes' }] },
      { type: 'horizontalRule' },
      { type: 'paragraph', content: [{ type: 'text', text: 'Depois' }] },
    ])
  })

  it('supports nested lists inside a list item', () => {
    const doc = markdownToTiptap('- Item\n  - Subitem\n')
    const [bulletList] = doc.content
    expect(bulletList.content?.[0].content).toEqual([
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
    ])
  })

  it('never interprets raw HTML — it stays as a literal text node, never markup', () => {
    const doc = markdownToTiptap(
      '<blockquote class="dica"><p><strong>Dica</strong>: cuidado.</p></blockquote>',
    )
    // A saída é um nó de texto puro contendo as tags como caracteres —
    // o Tiptap nunca interpreta isso como marcação (sem risco de XSS),
    // ao contrário de um `type: "html"` ou nó equivalente.
    expect(doc.content).toEqual([
      {
        type: 'paragraph',
        content: [
          {
            type: 'text',
            text: '<blockquote class="dica"><p><strong>Dica</strong>: cuidado.</p></blockquote>',
          },
        ],
      },
    ])
  })

  it('falls back to a visible placeholder for an image mixed with inline text', () => {
    const doc = markdownToTiptap('Antes ![alt](https://exemplo.org/x.png) depois')
    const [paragraph] = doc.content
    expect(paragraph.content).toEqual([
      { type: 'text', text: 'Antes ' },
      { type: 'text', text: '[imagem: alt]' },
      { type: 'text', text: ' depois' },
    ])
  })

  it('falls back to raw source text for an unsupported fenced code block, without crashing', () => {
    const doc = markdownToTiptap('```js\nconsole.log(1)\n```')
    expect(doc.content).toEqual([
      { type: 'paragraph', content: [{ type: 'text', text: 'console.log(1)' }] },
    ])
  })

  it('returns an empty paragraph for an empty document', () => {
    const doc = markdownToTiptap('')
    expect(doc).toEqual({ type: 'doc', content: [{ type: 'paragraph' }] })
  })
})
