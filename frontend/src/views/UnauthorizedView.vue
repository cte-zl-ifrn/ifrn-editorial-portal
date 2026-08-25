<script setup lang="ts">
import { useSession } from '../composables/useSession'
import StatusMessage from '../components/StatusMessage.vue'

const { user, repositoryPermission, logout } = useSession()
</script>

<template>
  <main class="unauthorized">
    <h1>Acesso não autorizado</h1>
    <StatusMessage kind="error">
      Olá, {{ user?.login }}. Sua permissão atual no repositório
      <code>cte-zl-ifrn/central-ajuda</code>
      <template v-if="repositoryPermission"> ({{ repositoryPermission }})</template>
      não permite usar o portal. Solicite permissão de escrita (<code>write</code>,
      <code>maintain</code> ou <code>admin</code>) no repositório.
    </StatusMessage>
    <button type="button" @click="logout">Sair</button>
  </main>
</template>

<style scoped>
.unauthorized {
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
