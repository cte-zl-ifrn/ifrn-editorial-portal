<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useSession } from '../composables/useSession'
import { useSampleDocument } from '../composables/useSampleDocument'
import { tiptapToMarkdown } from '../lib/tiptapToMarkdown'
import StatusMessage from '../components/StatusMessage.vue'
import FrontMatterPanel from '../components/FrontMatterPanel.vue'
import DocumentViewer from '../components/DocumentViewer.vue'
import type { TiptapDocument } from '../types/tiptap'

const { user, logout } = useSession()
const { status, document, errorMessage, load } = useSampleDocument()

onMounted(load)

const currentDoc = ref<TiptapDocument | null>(null)

function handleContentUpdate(doc: TiptapDocument): void {
  currentDoc.value = doc
}

/**
 * Prévia do documento resultante: front_matter_raw (inalterado) + corpo
 * serializado a partir do estado atual do Tiptap — nunca uma
 * reserialização do front matter (ver ADR-0009). Nada aqui é enviado ao
 * backend ou ao GitHub; é só para inspeção manual (Fase 2.2.5).
 */
const preview = computed<{ markdown: string; error: string | null }>(() => {
  if (!document.value || !currentDoc.value) return { markdown: '', error: null }
  try {
    const body = tiptapToMarkdown(currentDoc.value)
    return { markdown: document.value.front_matter_raw + body, error: null }
  } catch (error) {
    return { markdown: '', error: error instanceof Error ? error.message : 'Erro desconhecido.' }
  }
})
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
      <h2 id="sample-document-heading">Documento de demonstração (Fase 2.2 — edição, nada é salvo)</h2>

      <StatusMessage v-if="status === 'loading'">Carregando documento…</StatusMessage>

      <StatusMessage v-else-if="status === 'error'" kind="error">
        Não foi possível carregar o documento: {{ errorMessage }}
      </StatusMessage>

      <div v-else-if="status === 'loaded' && document" class="document">
        <p class="document__path"><code>{{ document.path }}</code></p>
        <FrontMatterPanel :front-matter="document.front_matter" />
        <DocumentViewer
          :markdown="document.body"
          editable
          @update:content="handleContentUpdate"
        />
      </div>
    </section>

    <section v-if="status === 'loaded' && document" aria-labelledby="preview-heading">
      <h2 id="preview-heading">Prévia do Markdown resultante (não salvo em nenhum lugar)</h2>

      <StatusMessage v-if="preview.error" kind="error">
        Não foi possível gerar a prévia: {{ preview.error }}
      </StatusMessage>
      <pre v-else class="preview">{{ preview.markdown }}</pre>
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

.preview {
  white-space: pre-wrap;
  background-color: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1rem;
  font-size: 0.85rem;
}

button {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  border: 1px solid #6b7280;
  background: transparent;
  cursor: pointer;
}
</style>
