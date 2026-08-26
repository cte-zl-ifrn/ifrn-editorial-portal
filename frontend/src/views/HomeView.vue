<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useSession } from '../composables/useSession'
import { useSampleDocument } from '../composables/useSampleDocument'
import { useSubmission } from '../composables/useSubmission'
import { tiptapToMarkdown } from '../lib/tiptapToMarkdown'
import { resolvePendingAssets } from '../lib/pendingAssets'
import StatusMessage from '../components/StatusMessage.vue'
import FrontMatterPanel from '../components/FrontMatterPanel.vue'
import DocumentViewer from '../components/DocumentViewer.vue'
import type { TiptapDocument } from '../types/tiptap'
import type { SubmissionAsset } from '../types'

const { user, logout } = useSession()
const { status, document, errorMessage, load } = useSampleDocument()

onMounted(load)

const currentDoc = ref<TiptapDocument | null>(null)

function handleContentUpdate(doc: TiptapDocument): void {
  currentDoc.value = doc
}

/**
 * Substitui imagens de upload local (data: URL) pela URL absoluta final
 * (raw.githubusercontent.com, não caminho relativo — ver ADR-0007) e
 * extrai o conteúdo binário como assets pendentes (Fase 3.2) —
 * calculado uma única vez por edição, e reaproveitado tanto
 * na prévia quanto no envio, para que os nomes de arquivo (que incluem um
 * id aleatório) sejam exatamente os mesmos nos dois lugares.
 */
const resolvedSubmission = computed<{ doc: TiptapDocument; assets: SubmissionAsset[] } | null>(
  () => {
    if (!currentDoc.value || !document.value) return null
    return resolvePendingAssets(currentDoc.value, document.value.path)
  },
)

/**
 * Corpo serializado a partir do estado atual do Tiptap — sem front
 * matter (ver ADR-0009). Usado tanto na prévia quanto no envio da
 * submissão (Fase 3.1); o backend relê o front matter fresco, nunca
 * confia no que o cliente envia (ver ADR-0011).
 */
const serializedBody = computed<{ markdown: string | null; error: string | null }>(() => {
  if (!resolvedSubmission.value) return { markdown: null, error: null }
  try {
    return { markdown: tiptapToMarkdown(resolvedSubmission.value.doc), error: null }
  } catch (error) {
    return { markdown: null, error: error instanceof Error ? error.message : 'Erro desconhecido.' }
  }
})

/**
 * Prévia do documento resultante: front_matter_raw (inalterado) + corpo
 * serializado, já com os caminhos finais dos assets. Nada aqui é enviado
 * ao backend ou ao GitHub por si só; é só para inspeção manual (Fase
 * 2.2.5 / Fase 3.2.5).
 */
const preview = computed<{ markdown: string; error: string | null }>(() => {
  if (!document.value || serializedBody.value.markdown === null) {
    return { markdown: '', error: serializedBody.value.error }
  }
  return { markdown: document.value.front_matter_raw + serializedBody.value.markdown, error: null }
})

const summary = ref('')
const {
  status: submissionStatus,
  result: submissionResult,
  errorMessage: submissionError,
  submit: submitChange,
} = useSubmission()

async function handleSubmit(): Promise<void> {
  if (!document.value || serializedBody.value.markdown === null || !resolvedSubmission.value) {
    return
  }
  await submitChange({
    body: serializedBody.value.markdown,
    base_sha: document.value.sha,
    summary: summary.value,
    assets: resolvedSubmission.value.assets,
  })
}
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
      <h2 id="sample-document-heading">Documento de demonstração (Fase 3.2 — envio com imagens via Pull Request)</h2>

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
      <h2 id="preview-heading">Prévia do Markdown resultante</h2>

      <StatusMessage v-if="preview.error" kind="error">
        Não foi possível gerar a prévia: {{ preview.error }}
      </StatusMessage>
      <pre v-else class="preview">{{ preview.markdown }}</pre>
    </section>

    <section v-if="status === 'loaded' && document" aria-labelledby="submit-heading">
      <h2 id="submit-heading">Enviar alteração</h2>

      <div class="submit-form">
        <label for="summary">Resumo da alteração</label>
        <textarea
          id="summary"
          v-model="summary"
          rows="3"
          placeholder="Descreva o que foi alterado e por quê"
          :disabled="submissionStatus === 'submitting'"
        ></textarea>
        <button
          type="button"
          :disabled="submissionStatus === 'submitting' || !summary.trim() || !!preview.error"
          @click="handleSubmit"
        >
          {{ submissionStatus === 'submitting' ? 'Enviando…' : 'Enviar alteração' }}
        </button>
      </div>

      <StatusMessage v-if="submissionStatus === 'success' && submissionResult">
        Pull Request criado:
        <a :href="submissionResult.pull_request.html_url" target="_blank" rel="noopener noreferrer">
          #{{ submissionResult.pull_request.number }}
        </a>
        (branch <code>{{ submissionResult.branch }}</code>)
      </StatusMessage>

      <StatusMessage v-else-if="submissionStatus === 'conflict'" kind="error">
        O documento foi alterado no repositório desde que você começou a editar.
        Recarregue a página para obter a versão mais recente antes de enviar de novo.
      </StatusMessage>

      <StatusMessage v-else-if="submissionStatus === 'error'" kind="error">
        Não foi possível enviar a alteração: {{ submissionError }}
      </StatusMessage>
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

.submit-form {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.submit-form textarea {
  font-family: inherit;
  padding: 0.5rem;
  border-radius: 0.5rem;
  border: 1px solid #d1d5db;
}

.submit-form button {
  align-self: flex-start;
}

button {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  border: 1px solid #6b7280;
  background: transparent;
  cursor: pointer;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
