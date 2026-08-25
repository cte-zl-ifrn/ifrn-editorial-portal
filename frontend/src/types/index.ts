/**
 * Tipos espelham docs/api/openapi.yaml (Fase 1).
 */

export interface GithubUser {
  login: string
  name: string | null
  avatar_url: string | null
}

export interface MeResponse {
  user: GithubUser
  authorized: boolean
  repository_permission: string | null
}

export interface DocumentResponse {
  path: string
  name: string
  content: string
  sha: string
  encoding: string
}

export interface ApiErrorBody {
  error: string
  message?: string
  correlation_id?: string
}

export class ApiError extends Error {
  readonly status: number
  readonly code: string
  readonly correlationId?: string

  constructor(status: number, body: ApiErrorBody) {
    super(body.message ?? body.error)
    this.status = status
    this.code = body.error
    this.correlationId = body.correlation_id
  }
}
