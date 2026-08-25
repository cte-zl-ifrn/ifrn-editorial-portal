<script setup lang="ts">
import { RouterView } from 'vue-router'
import { useSession } from './composables/useSession'
import StatusMessage from './components/StatusMessage.vue'

const { status, errorMessage, refresh } = useSession()
</script>

<template>
  <div id="app-shell">
    <StatusMessage v-if="status === 'loading'">Carregando…</StatusMessage>

    <div v-else-if="status === 'error'" class="app-error">
      <StatusMessage kind="error">
        Erro de comunicação com a API{{ errorMessage ? `: ${errorMessage}` : '.' }}
      </StatusMessage>
      <button type="button" @click="refresh">Tentar novamente</button>
    </div>

    <RouterView v-else />
  </div>
</template>

<style scoped>
#app-shell {
  min-height: 100vh;
}

.app-error {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 1rem;
  max-width: 32rem;
  margin: 4rem auto;
}

button {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  border: 1px solid #6b7280;
  background: transparent;
  cursor: pointer;
}
</style>
