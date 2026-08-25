import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import { router } from './router'

const app = createApp(App)
app.use(router)

// Aguarda a navegação inicial (que já resolve o estado de sessão via
// guarda de rota) antes de montar, para evitar um flash de conteúdo
// incorreto — ver src/router/index.ts.
router.isReady().then(() => {
  app.mount('#app')
})
