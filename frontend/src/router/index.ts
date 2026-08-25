import { createRouter, createWebHistory } from 'vue-router'
import { useSession } from '../composables/useSession'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import UnauthorizedView from '../views/UnauthorizedView.vue'

export const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/login', name: 'login', component: LoginView },
    { path: '/unauthorized', name: 'unauthorized', component: UnauthorizedView },
  ],
})

/**
 * Redireciona conforme o estado de sessão (ver
 * docs/architecture/authorization-model.md). Estados de carregamento e
 * erro são tratados em App.vue, sobrepostos a qualquer rota.
 */
router.beforeEach(async (to) => {
  const { status, ensureSessionLoaded } = useSession()
  await ensureSessionLoaded()

  if (status.value === 'unauthenticated' && to.name !== 'login') {
    return { name: 'login' }
  }
  if (status.value === 'unauthorized' && to.name !== 'unauthorized') {
    return { name: 'unauthorized' }
  }
  if (status.value === 'authorized' && to.name !== 'home') {
    return { name: 'home' }
  }
  return true
})
