import { describe, expect, it, vi, beforeEach } from 'vitest'
import { apiFetch, API_BASE_URL } from '../src/services/apiClient'
import { ApiError } from '../src/types'

describe('apiFetch', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('sends credentials: include and returns parsed JSON on success', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ status: 'ok' }), { status: 200 }),
    )
    vi.stubGlobal('fetch', fetchMock)

    const result = await apiFetch<{ status: string }>('/health')

    expect(result).toEqual({ status: 'ok' })
    expect(fetchMock).toHaveBeenCalledWith(
      `${API_BASE_URL}/health`,
      expect.objectContaining({ credentials: 'include' }),
    )
  })

  it('always sends the X-Portal-Client header (ADR-0014)', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ status: 'ok' }), { status: 200 }),
    )
    vi.stubGlobal('fetch', fetchMock)

    await apiFetch<{ status: string }>('/api/submissions', { method: 'POST' })

    expect(fetchMock).toHaveBeenCalledWith(
      `${API_BASE_URL}/api/submissions`,
      expect.objectContaining({
        headers: expect.objectContaining({ 'X-Portal-Client': '1' }),
      }),
    )
  })

  it('throws ApiError with the error code from the response body', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ error: 'unauthenticated', message: 'Sem sessão.' }), {
        status: 401,
      }),
    )
    vi.stubGlobal('fetch', fetchMock)

    await expect(apiFetch('/api/me')).rejects.toMatchObject({
      status: 401,
      code: 'unauthenticated',
    })
  })

  it('treats 204 responses as no content', async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(null, { status: 204 }))
    vi.stubGlobal('fetch', fetchMock)

    const result = await apiFetch<void>('/auth/logout', { method: 'POST' })

    expect(result).toBeUndefined()
  })

  it('re-exports ApiError as a real Error subclass', () => {
    const error = new ApiError(403, { error: 'unauthorized' })
    expect(error).toBeInstanceOf(Error)
    expect(error.status).toBe(403)
  })
})
