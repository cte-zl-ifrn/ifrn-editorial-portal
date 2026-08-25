import { describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'

vi.mock('../src/services/authService', () => ({
  startLogin: vi.fn(),
}))

import { startLogin } from '../src/services/authService'
import LoginView from '../src/views/LoginView.vue'

describe('LoginView', () => {
  it('starts the login redirect when the button is clicked', async () => {
    const wrapper = mount(LoginView)

    await wrapper.get('button').trigger('click')

    expect(startLogin).toHaveBeenCalledOnce()
  })
})
