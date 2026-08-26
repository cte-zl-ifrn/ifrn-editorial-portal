import { ref, readonly } from 'vue'
import { createSubmission } from '../services/submissionService'
import { ApiError } from '../types'
import type { SubmissionRequest, SubmissionResponse } from '../types'

export type SubmissionStatus = 'idle' | 'submitting' | 'success' | 'conflict' | 'error'

export function useSubmission() {
  const status = ref<SubmissionStatus>('idle')
  const result = ref<SubmissionResponse | null>(null)
  const errorMessage = ref<string | null>(null)

  async function submit(payload: SubmissionRequest): Promise<void> {
    status.value = 'submitting'
    errorMessage.value = null
    result.value = null
    try {
      result.value = await createSubmission(payload)
      status.value = 'success'
    } catch (error) {
      status.value = error instanceof ApiError && error.code === 'document_conflict'
        ? 'conflict'
        : 'error'
      errorMessage.value = error instanceof Error ? error.message : 'Erro desconhecido.'
    }
  }

  function reset(): void {
    status.value = 'idle'
    result.value = null
    errorMessage.value = null
  }

  return {
    status: readonly(status),
    result: readonly(result),
    errorMessage: readonly(errorMessage),
    submit,
    reset,
  }
}
