import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import FrontMatterPanel from '../src/components/FrontMatterPanel.vue'

describe('FrontMatterPanel', () => {
  it('renders each front matter field as a term/definition pair', () => {
    const wrapper = mount(FrontMatterPanel, {
      props: {
        frontMatter: { title: 'Como acessar o Moodle', category: 'moodle', tags: ['a', 'b'] },
      },
    })

    const text = wrapper.text()
    expect(text).toContain('title')
    expect(text).toContain('Como acessar o Moodle')
    expect(text).toContain('category')
    expect(text).toContain('moodle')
    expect(text).toContain('a, b')
  })

  it('shows a message when there is no front matter', () => {
    const wrapper = mount(FrontMatterPanel, { props: { frontMatter: {} } })

    expect(wrapper.text()).toContain('não possui front matter')
  })
})
