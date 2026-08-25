import { describe, expect, it, vi } from 'vitest'

vi.mock('../src/services/documentService', () => ({
  fetchSampleDocument: vi.fn(),
}))

import { fetchSampleDocument } from '../src/services/documentService'
import { useSampleDocument } from '../src/composables/useSampleDocument'

describe('useSampleDocument', () => {
  it('loads the sample document successfully', async () => {
    vi.mocked(fetchSampleDocument).mockResolvedValue({
      path: '_docs/ambiente-virtual/acesso-moodle.md',
      name: 'acesso-moodle.md',
      content: '# Como acessar o Moodle',
      sha: 'abc123',
      encoding: 'utf-8',
    })

    const { load, status, document } = useSampleDocument()
    await load()

    expect(status.value).toBe('loaded')
    expect(document.value?.name).toBe('acesso-moodle.md')
  })

  it('reports an error state when the request fails', async () => {
    vi.mocked(fetchSampleDocument).mockRejectedValue(new Error('falha de rede'))

    const { load, status, errorMessage } = useSampleDocument()
    await load()

    expect(status.value).toBe('error')
    expect(errorMessage.value).toBe('falha de rede')
  })
})
