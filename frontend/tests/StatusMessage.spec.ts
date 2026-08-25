import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import StatusMessage from '../src/components/StatusMessage.vue'

describe('StatusMessage', () => {
  it('renders the slot content with role=alert', () => {
    const wrapper = mount(StatusMessage, {
      slots: { default: 'Algo deu errado' },
    })

    expect(wrapper.attributes('role')).toBe('alert')
    expect(wrapper.text()).toContain('Algo deu errado')
  })

  it('defaults to the info kind', () => {
    const wrapper = mount(StatusMessage)
    expect(wrapper.classes()).toContain('status-message--info')
  })

  it('applies the error kind when requested', () => {
    const wrapper = mount(StatusMessage, { props: { kind: 'error' } })
    expect(wrapper.classes()).toContain('status-message--error')
  })
})
