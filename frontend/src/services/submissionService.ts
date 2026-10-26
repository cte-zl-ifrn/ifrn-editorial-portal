import { apiFetch } from './apiClient'
import type { SubmissionRequest, SubmissionResponse } from '../types'

/**
 * Envia a submissão de escrita (Fase 3.1) — cria branch, commit e Pull
 * Request no backend. `base_sha` é o `sha` do documento no momento em
 * que foi carregado; se o arquivo mudou no repositório desde então, o
 * backend responde com um erro de conflito (`document_conflict`, 409).
 */
export function createSubmission(payload: SubmissionRequest): Promise<SubmissionResponse> {
  return apiFetch<SubmissionResponse>('/api/submissions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}
