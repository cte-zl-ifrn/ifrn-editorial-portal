import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import type { Editor } from '@tiptap/vue-3'
import DocumentViewer from '../src/components/DocumentViewer.vue'

/**
 * O evento `create` do Tiptap é agendado com `window.setTimeout(..., 0)`
 * internamente (ver @tiptap/core Editor.ts) — uma macrotask, não uma
 * microtask. `nextTick`/`flushPromises` não são suficientes para
 * aguardá-lo; é preciso ceder o loop de eventos de verdade.
 */
function waitForEditorCreate(): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, 0))
}

describe('DocumentViewer', () => {
  it('renders the converted Markdown content read-only', async () => {
    const wrapper = mount(DocumentViewer, {
      props: { markdown: '# Título\n\nUm parágrafo com **negrito**.' },
    })
    await nextTick()
    await nextTick()

    expect(wrapper.find('h1').text()).toBe('Título')
    expect(wrapper.find('strong').text()).toBe('negrito')

    const editableRoot = wrapper.find('[contenteditable]')
    expect(editableRoot.attributes('contenteditable')).toBe('false')
  })

  it('re-renders when the markdown prop changes', async () => {
    const wrapper = mount(DocumentViewer, { props: { markdown: '# Um' } })
    await nextTick()
    await nextTick()
    expect(wrapper.find('h1').text()).toBe('Um')

    await wrapper.setProps({ markdown: '# Dois' })
    await nextTick()
    await nextTick()

    expect(wrapper.find('h1').text()).toBe('Dois')
  })

  it('becomes editable when the editable prop is true, and shows the toolbar', async () => {
    const wrapper = mount(DocumentViewer, {
      props: { markdown: 'Um parágrafo.', editable: true },
    })
    await nextTick()
    await nextTick()

    const editableRoot = wrapper.find('[contenteditable]')
    expect(editableRoot.attributes('contenteditable')).toBe('true')
    expect(wrapper.find('[role="toolbar"]').exists()).toBe(true)
  })

  it('emits update:content with the current Tiptap JSON as soon as the editor is created', async () => {
    const wrapper = mount(DocumentViewer, {
      props: { markdown: '# Título', editable: true },
    })
    await waitForEditorCreate()

    const events = wrapper.emitted('update:content')
    expect(events).toBeTruthy()
    expect(events?.[0]?.[0]).toEqual({
      type: 'doc',
      content: [{ type: 'heading', attrs: { level: 1 }, content: [{ type: 'text', text: 'Título' }] }],
    })
  })

  it('applying bold via the toolbar toggles the mark and emits an updated document', async () => {
    const wrapper = mount(DocumentViewer, {
      props: { markdown: 'texto', editable: true },
    })
    await nextTick()
    await nextTick()

    const editor = (wrapper.vm as unknown as { editor: Editor }).editor
    // Seleciona todo o conteúdo, simulando o que o usuário faria
    // selecionando o texto na tela antes de clicar em "negrito".
    editor.commands.selectAll()

    const boldButton = wrapper.findAll('button').find((button) => button.text() === 'N')
    expect(boldButton).toBeTruthy()
    await boldButton!.trigger('click')
    await nextTick()

    expect(editor.isActive('bold')).toBe(true)
    const lastEmitted = wrapper.emitted('update:content')?.at(-1)?.[0]
    expect(JSON.stringify(lastEmitted)).toContain('"bold"')
  })
})
