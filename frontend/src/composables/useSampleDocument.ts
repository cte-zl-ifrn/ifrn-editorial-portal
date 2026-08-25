import { ref, readonly } from 'vue'
import { fetchSampleDocument } from '../services/documentService'
import type { DocumentResponse } from '../types'

export type DocumentStatus = 'idle' | 'loading' | 'loaded' | 'error'

export function useSampleDocument() {
  const status = ref<DocumentStatus>('idle')
  const document = ref<DocumentResponse | null>(null)
  const errorMessage = ref<string | null>(null)

  async function load(): Promise<void> {
    status.value = 'loading'
    errorMessage.value = null
    try {
      document.value = await fetchSampleDocument()
      status.value = 'loaded'
    } catch (error) {
      status.value = 'error'
      errorMessage.value = error instanceof Error ? error.message : 'Erro desconhecido.'
    }
  }

  return {
    status: readonly(status),
    document: readonly(document),
    errorMessage: readonly(errorMessage),
    load,
  }
}
