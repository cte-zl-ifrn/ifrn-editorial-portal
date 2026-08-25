import { apiFetch, API_BASE_URL } from './apiClient'
import type { MeResponse } from '../types'

/**
 * O login é sempre um redirecionamento de navegador para o backend — o
 * frontend nunca troca código/tokens do GitHub diretamente (ver
 * docs/architecture/authentication-flow.md).
 */
export function loginUrl(): string {
  return `${API_BASE_URL}/auth/login`
}

export function startLogin(): void {
  window.location.href = loginUrl()
}

export function fetchMe(): Promise<MeResponse> {
  return apiFetch<MeResponse>('/api/me')
}

export async function logout(): Promise<void> {
  await apiFetch<void>('/auth/logout', { method: 'POST' })
}
