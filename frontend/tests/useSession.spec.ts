import { describe, expect, it, vi, beforeEach } from 'vitest'
import { ApiError } from '../src/types'

vi.mock('../src/services/authService', () => ({
  fetchMe: vi.fn(),
  logout: vi.fn(),
}))

import { fetchMe, logout as logoutRequest } from '../src/services/authService'
import { useSession } from '../src/composables/useSession'

describe('useSession', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('marks the session as authorized when the backend says so', async () => {
    vi.mocked(fetchMe).mockResolvedValue({
      user: { login: 'maria.silva', name: 'Maria Silva', avatar_url: null },
      authorized: true,
      repository_permission: 'write',
    })

    const { refresh, status, user } = useSession()
    await refresh()

    expect(status.value).toBe('authorized')
    expect(user.value?.login).toBe('maria.silva')
  })

  it('marks the session as unauthorized when the backend says so', async () => {
    vi.mocked(fetchMe).mockResolvedValue({
      user: { login: 'maria.silva', name: null, avatar_url: null },
      authorized: false,
      repository_permission: 'read',
    })

    const { refresh, status } = useSession()
    await refresh()

    expect(status.value).toBe('unauthorized')
  })

  it('marks the session as unauthenticated on a 401 response', async () => {
    vi.mocked(fetchMe).mockRejectedValue(new ApiError(401, { error: 'unauthenticated' }))

    const { refresh, status } = useSession()
    await refresh()

    expect(status.value).toBe('unauthenticated')
  })

  it('marks the session as an error on unexpected failures', async () => {
    vi.mocked(fetchMe).mockRejectedValue(new Error('network down'))

    const { refresh, status, errorMessage } = useSession()
    await refresh()

    expect(status.value).toBe('error')
    expect(errorMessage.value).toBe('network down')
  })

  it('resets to unauthenticated after logout', async () => {
    vi.mocked(fetchMe).mockResolvedValue({
      user: { login: 'maria.silva', name: null, avatar_url: null },
      authorized: true,
      repository_permission: 'write',
    })
    vi.mocked(logoutRequest).mockResolvedValue(undefined)

    const { refresh, logout, status, user } = useSession()
    await refresh()
    await logout()

    expect(status.value).toBe('unauthenticated')
    expect(user.value).toBeNull()
  })
})
