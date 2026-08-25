import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import DocumentViewer from '../src/components/DocumentViewer.vue'

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
})
