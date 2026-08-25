<script setup lang="ts">
import { onMounted } from 'vue'
import { useSession } from '../composables/useSession'
import { useSampleDocument } from '../composables/useSampleDocument'
import StatusMessage from '../components/StatusMessage.vue'

const { user, logout } = useSession()
const { status, document, errorMessage, load } = useSampleDocument()

onMounted(load)
</script>

<template>
  <main class="home">
    <header class="home__header">
      <div>
        <h1>Portal Editorial IFRN</h1>
        <p>Autenticado como <strong>{{ user?.login }}</strong></p>
      </div>
      <button type="button" @click="logout">Sair</button>
    </header>

    <section aria-labelledby="sample-document-heading">
      <h2 id="sample-document-heading">Documento de demonstração (Fase 1)</h2>

      <StatusMessage v-if="status === 'loading'">Carregando documento…</StatusMessage>

      <StatusMessage v-else-if="status === 'error'" kind="error">
        Não foi possível carregar o documento: {{ errorMessage }}
      </StatusMessage>

      <article v-else-if="status === 'loaded' && document" class="document">
        <p class="document__path"><code>{{ document.path }}</code></p>
        <pre class="document__content">{{ document.content }}</pre>
      </article>
    </section>
  </main>
</template>

<style scoped>
.home {
  max-width: 48rem;
  margin: 2rem auto;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.home__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.document__path {
  color: #6b7280;
}

.document__content {
  white-space: pre-wrap;
  background-color: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1rem;
}

button {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  border: 1px solid #6b7280;
  background: transparent;
  cursor: pointer;
}
</style>
