/**
 * Tipos espelham docs/api/openapi.yaml (Fase 1 / Fase 2.1 / Fase 3.1).
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

/**
 * front_matter_raw + body reproduz o arquivo original (ver ADR-0009);
 * front_matter é o mesmo conteúdo já parseado, só para exibição.
 */
export interface DocumentResponse {
  path: string
  name: string
  sha: string
  front_matter: Record<string, unknown>
  front_matter_raw: string
  body: string
}

/**
 * `body` é o Markdown já serializado pelo frontend (sem front matter —
 * o backend relê o original no momento da gravação, ver ADR-0011).
 */
export interface SubmissionRequest {
  body: string
  base_sha: string
  summary: string
}

export interface PullRequestInfo {
  number: number
  html_url: string
  state: string
}

export interface SubmissionResponse {
  submission_id: string
  branch: string
  pull_request: PullRequestInfo
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
