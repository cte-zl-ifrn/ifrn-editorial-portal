import { describe, expect, it, vi, beforeEach } from 'vitest'
import { createSubmission } from '../src/services/submissionService'
import { API_BASE_URL } from '../src/services/apiClient'

describe('createSubmission', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('POSTs the payload as JSON to /api/submissions with credentials included', async () => {
    const responseBody = {
      submission_id: 'a1b2c3d4',
      branch: 'portal/update/2026/a1b2c3d4-como-fazer-cursos',
      pull_request: {
        number: 42,
        html_url: 'https://github.com/cte-zl-ifrn/central-ajuda/pull/42',
        state: 'open',
      },
    }
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify(responseBody), { status: 201 }))
    vi.stubGlobal('fetch', fetchMock)

    const payload = { body: '# Novo corpo', base_sha: 'abc123', summary: 'Corrige um typo.' }
    const result = await createSubmission(payload)

    expect(result).toEqual(responseBody)
    expect(fetchMock).toHaveBeenCalledWith(
      `${API_BASE_URL}/api/submissions`,
      expect.objectContaining({
        method: 'POST',
        credentials: 'include',
        body: JSON.stringify(payload),
      }),
    )
  })
})
