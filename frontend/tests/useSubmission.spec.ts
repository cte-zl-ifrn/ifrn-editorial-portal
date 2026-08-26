import { describe, expect, it, vi, beforeEach } from 'vitest'
import { ApiError } from '../src/types'

vi.mock('../src/services/submissionService', () => ({
  createSubmission: vi.fn(),
}))

import { createSubmission } from '../src/services/submissionService'
import { useSubmission } from '../src/composables/useSubmission'

const PAYLOAD = { body: '# Novo corpo', base_sha: 'abc123', summary: 'Corrige um typo.' }

describe('useSubmission', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('marks the submission as successful and stores the result', async () => {
    vi.mocked(createSubmission).mockResolvedValue({
      submission_id: 'a1b2c3d4',
      branch: 'portal/update/2026/a1b2c3d4-como-fazer-cursos',
      pull_request: {
        number: 42,
        html_url: 'https://github.com/cte-zl-ifrn/central-ajuda/pull/42',
        state: 'open',
      },
    })

    const { submit, status, result } = useSubmission()
    await submit(PAYLOAD)

    expect(status.value).toBe('success')
    expect(result.value?.pull_request.number).toBe(42)
  })

  it('marks the submission as a conflict on a document_conflict API error', async () => {
    vi.mocked(createSubmission).mockRejectedValue(
      new ApiError(409, { error: 'document_conflict', message: 'Documento mudou.' }),
    )

    const { submit, status, errorMessage } = useSubmission()
    await submit(PAYLOAD)

    expect(status.value).toBe('conflict')
    expect(errorMessage.value).toBe('Documento mudou.')
  })

  it('marks the submission as a generic error for any other failure', async () => {
    vi.mocked(createSubmission).mockRejectedValue(
      new ApiError(502, { error: 'github_communication_error' }),
    )

    const { submit, status } = useSubmission()
    await submit(PAYLOAD)

    expect(status.value).toBe('error')
  })

  it('resets to idle, clearing the previous result', async () => {
    vi.mocked(createSubmission).mockResolvedValue({
      submission_id: 'x',
      branch: 'portal/update/2026/x-doc',
      pull_request: { number: 1, html_url: 'https://x', state: 'open' },
    })

    const { submit, reset, status, result } = useSubmission()
    await submit(PAYLOAD)
    reset()

    expect(status.value).toBe('idle')
    expect(result.value).toBeNull()
  })
})
