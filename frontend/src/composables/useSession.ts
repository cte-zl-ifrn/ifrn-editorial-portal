import { ref, readonly } from 'vue'
import { fetchMe, logout as logoutRequest } from '../services/authService'
import { ApiError } from '../types'
import type { GithubUser } from '../types'

export type SessionStatus =
  | 'loading'
  | 'unauthenticated'
  | 'unauthorized'
  | 'authorized'
  | 'error'

const status = ref<SessionStatus>('loading')
const user = ref<GithubUser | null>(null)
const repositoryPermission = ref<string | null>(null)
const errorMessage = ref<string | null>(null)

async function refresh(): Promise<void> {
  status.value = 'loading'
  errorMessage.value = null
  try {
    const me = await fetchMe()
    user.value = me.user
    repositoryPermission.value = me.repository_permission
    status.value = me.authorized ? 'authorized' : 'unauthorized'
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      status.value = 'unauthenticated'
      user.value = null
    } else {
      status.value = 'error'
      errorMessage.value = error instanceof Error ? error.message : 'Erro desconhecido.'
    }
  }
}

async function logout(): Promise<void> {
  await logoutRequest()
  user.value = null
  repositoryPermission.value = null
  status.value = 'unauthenticated'
  sessionPromise = null
}

let sessionPromise: Promise<void> | null = null

/**
 * Garante que a sessão foi consultada ao menos uma vez, reaproveitando a
 * mesma promessa em chamadas concorrentes (ex.: guarda de rota inicial).
 */
function ensureSessionLoaded(): Promise<void> {
  if (!sessionPromise) {
    sessionPromise = refresh()
  }
  return sessionPromise
}

/**
 * Estado de sessão compartilhado entre componentes (singleton simples,
 * suficiente para o escopo da Fase 1 — sem gerenciador de estado
 * dedicado).
 */
export function useSession() {
  return {
    status: readonly(status),
    user: readonly(user),
    repositoryPermission: readonly(repositoryPermission),
    errorMessage: readonly(errorMessage),
    refresh,
    logout,
    ensureSessionLoaded,
  }
}
