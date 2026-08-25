import { ApiError, type ApiErrorBody } from '../types'

/**
 * URL base do backend. Nunca embuta segredos — apenas configuração pública
 * (ver docs/requirements/non-functional-requirements.md, RNF-21).
 */
export const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

/**
 * Envia sempre `credentials: "include"` para que o cookie de sessão
 * HttpOnly criado pelo backend seja enviado nas requisições — ver
 * docs/architecture/authentication-flow.md.
 */
export async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    credentials: 'include',
    headers: {
      Accept: 'application/json',
      ...init.headers,
    },
  })

  if (response.status === 204) {
    return undefined as T
  }

  const body = await response.json().catch(() => null)

  if (!response.ok) {
    const errorBody: ApiErrorBody = body ?? { error: 'unknown_error' }
    throw new ApiError(response.status, errorBody)
  }

  return body as T
}
