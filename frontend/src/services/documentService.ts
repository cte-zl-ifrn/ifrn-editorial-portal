import { apiFetch } from './apiClient'
import type { DocumentResponse } from '../types'

/**
 * Lê o documento de demonstração fixo da Fase 1
 * (GET /api/documents/sample) — não é possível pedir outro caminho.
 */
export function fetchSampleDocument(): Promise<DocumentResponse> {
  return apiFetch<DocumentResponse>('/api/documents/sample')
}
