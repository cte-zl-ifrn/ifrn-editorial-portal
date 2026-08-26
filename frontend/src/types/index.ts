/**
 * Tipos espelham docs/api/openapi.yaml (Fase 1 / Fase 2.1 / Fase 3.1 / Fase 3.2).
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
 * Asset a gravar na mesma branch do documento (Fase 3.2, ver ADR-0007).
 * `filename` é só uma sugestão — o backend sempre valida antes de gravar
 * (ver backend/src/assets/validation.py).
 */
export interface SubmissionAsset {
  kind: 'image' | 'file'
  filename: string
  content: string
  alt?: string
}

/**
 * `body` é o Markdown já serializado pelo frontend (sem front matter —
 * o backend relê o original no momento da gravação, ver ADR-0011).
 */
export interface SubmissionRequest {
  body: string
  base_sha: string
  summary: string
  assets?: SubmissionAsset[]
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
  asset_paths: string[]
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
