<script setup lang="ts">
import { onMounted } from 'vue'
import { useSession } from '../composables/useSession'
import { useSampleDocument } from '../composables/useSampleDocument'
import StatusMessage from '../components/StatusMessage.vue'
import FrontMatterPanel from '../components/FrontMatterPanel.vue'
import DocumentViewer from '../components/DocumentViewer.vue'

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
      <h2 id="sample-document-heading">Documento de demonstração (Fase 2.1 — somente leitura)</h2>

      <StatusMessage v-if="status === 'loading'">Carregando documento…</StatusMessage>

      <StatusMessage v-else-if="status === 'error'" kind="error">
        Não foi possível carregar o documento: {{ errorMessage }}
      </StatusMessage>

      <div v-else-if="status === 'loaded' && document" class="document">
        <p class="document__path"><code>{{ document.path }}</code></p>
        <FrontMatterPanel :front-matter="document.front_matter" />
        <DocumentViewer :markdown="document.body" />
      </div>
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

.document {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.document__path {
  color: #6b7280;
}

button {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  border: 1px solid #6b7280;
  background: transparent;
  cursor: pointer;
}
</style>
