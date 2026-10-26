import { describe, expect, it, vi } from 'vitest'

vi.mock('../src/services/documentService', () => ({
  fetchSampleDocument: vi.fn(),
}))

import { fetchSampleDocument } from '../src/services/documentService'
import { useSampleDocument } from '../src/composables/useSampleDocument'

describe('useSampleDocument', () => {
  it('loads the sample document successfully', async () => {
    vi.mocked(fetchSampleDocument).mockResolvedValue({
      path: '_docs/proitec/como-fazer-cursos.md',
      name: 'como-fazer-cursos.md',
      sha: 'abc123',
      front_matter: { title: 'Como fazer os cursos do ProITEC?' },
      front_matter_raw: '---\ntitle: Como fazer os cursos do ProITEC?\n---\n',
      body: '# Como fazer os cursos do ProITEC?',
    })

    const { load, status, document } = useSampleDocument()
    await load()

    expect(status.value).toBe('loaded')
    expect(document.value?.name).toBe('como-fazer-cursos.md')
  })

  it('reports an error state when the request fails', async () => {
    vi.mocked(fetchSampleDocument).mockRejectedValue(new Error('falha de rede'))

    const { load, status, errorMessage } = useSampleDocument()
    await load()

    expect(status.value).toBe('error')
    expect(errorMessage.value).toBe('falha de rede')
  })
})
