import { describe, expect, it } from 'vitest'
import { markdownToTiptap } from '../src/lib/markdownToTiptap'
import { COMO_FAZER_CURSOS_BODY } from './fixtures/realDocuments'

describe('markdownToTiptap — documento real de demonstração', () => {
  it('converte o corpo inteiro sem lançar exceção', () => {
    expect(() => markdownToTiptap(COMO_FAZER_CURSOS_BODY)).not.toThrow()
  })

  it('produz uma árvore não vazia com os tipos de nó esperados', () => {
    const doc = markdownToTiptap(COMO_FAZER_CURSOS_BODY)
    const types = new Set(doc.content.map((node) => node.type))

    expect(doc.content.length).toBeGreaterThan(10)
    expect(types).toContain('heading')
    expect(types).toContain('bulletList')
    expect(types).toContain('orderedList')
    expect(types).toContain('horizontalRule')
  })

  it('preserva os blocos HTML crus como texto literal, sem quebrar a árvore', () => {
    const doc = markdownToTiptap(COMO_FAZER_CURSOS_BODY)
    const flatText = JSON.stringify(doc)

    expect(flatText).toContain('blockquote class=\\"dica\\"')
    expect(flatText).not.toContain('"type":"blockquote"')
  })

  it('preserva o link com sintaxe de template do Jekyll como href opaco', () => {
    const doc = markdownToTiptap(COMO_FAZER_CURSOS_BODY)
    const flatText = JSON.stringify(doc)

    expect(flatText).toContain('{{ site.baseurl }}/category/ambiente_virtual/')
  })
})
