<script setup lang="ts">
import { watch } from 'vue'
import { EditorContent, useEditor } from '@tiptap/vue-3'
import { markdownToTiptap } from '../lib/markdownToTiptap'
import { ACCEPTED_IMAGE_MIME_TYPES } from '../lib/pendingAssets'
import { tiptapExtensions } from '../lib/tiptapExtensions'
import type { TiptapDocument } from '../types/tiptap'

/**
 * Renderiza Markdown via Tiptap. Fase 2.1: `editable: false` (somente
 * leitura). Fase 2.2: `editable: true` habilita edição do corpo com uma
 * toolbar mínima — ver docs/phase-2.2-plan.md. Em ambos os casos, emite
 * o documento Tiptap atual (`update:content`) para que quem usa este
 * componente possa serializar de volta para Markdown (ex.: a prévia em
 * HomeView.vue), sem que este componente conheça o serializer.
 */
const props = withDefaults(
  defineProps<{
    markdown: string
    editable?: boolean
  }>(),
  { editable: false },
)

const emit = defineEmits<{
  'update:content': [doc: TiptapDocument]
}>()

const editor = useEditor({
  content: markdownToTiptap(props.markdown),
  editable: props.editable,
  extensions: tiptapExtensions,
  onCreate: ({ editor: instance }) => {
    emit('update:content', instance.getJSON() as TiptapDocument)
  },
  onUpdate: ({ editor: instance }) => {
    emit('update:content', instance.getJSON() as TiptapDocument)
  },
})

watch(
  () => props.markdown,
  (markdown) => {
    editor.value?.commands.setContent(markdownToTiptap(markdown))
  },
)

watch(
  () => props.editable,
  (editable) => {
    editor.value?.setEditable(editable)
  },
)

defineExpose({ editor })

function setLink(): void {
  const previousHref = editor.value?.getAttributes('link').href as string | undefined
  const href = window.prompt('URL do link:', previousHref ?? 'https://')
  if (href === null) return
  const chain = editor.value?.chain().focus().extendMarkRange('link')
  if (href === '') {
    chain?.unsetLink().run()
  } else {
    chain?.setLink({ href }).run()
  }
}

/**
 * Upload de arquivo local (Fase 3.2) — não mais uma URL já publicada
 * (comportamento da Fase 2.2). A imagem é inserida como uma `data:` URL
 * para prévia imediata; `resolvePendingAssets`
 * (`src/lib/pendingAssets.ts`) troca isso pela URL absoluta final e
 * extrai o conteúdo para envio como asset só no momento da prévia/envio
 * (ver HomeView.vue) — este componente não precisa saber nada sobre
 * caminhos de asset ou submissão.
 *
 * O atributo `accept` do input é só uma dica de UI — o sistema
 * operacional pode permitir escolher qualquer arquivo mesmo assim (ex.:
 * opção "todos os arquivos" no seletor). Por isso o `file.type` real é
 * conferido aqui antes de prosseguir; o backend também valida (assinatura
 * do arquivo, não só o tipo declarado) antes de gravar qualquer coisa.
 */
function setImage(): void {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = ACCEPTED_IMAGE_MIME_TYPES.join(',')
  input.addEventListener('change', () => {
    const file = input.files?.[0]
    if (!file) return
    if (!ACCEPTED_IMAGE_MIME_TYPES.includes(file.type)) {
      window.alert('Tipo de arquivo não suportado. Envie uma imagem PNG, JPEG, GIF ou WebP.')
      return
    }
    const alt = window.prompt('Texto alternativo (obrigatório para acessibilidade):')
    if (!alt) return
    const reader = new FileReader()
    reader.addEventListener('load', () => {
      const dataUrl = reader.result
      if (typeof dataUrl !== 'string') return
      editor.value?.chain().focus().setImage({ src: dataUrl, alt }).run()
    })
    reader.readAsDataURL(file)
  })
  input.click()
}
</script>

<template>
  <div class="document-viewer">
    <div v-if="editable" class="document-viewer__toolbar" role="toolbar" aria-label="Formatação">
      <button
        type="button"
        :aria-pressed="editor?.isActive('bold')"
        @click="editor?.chain().focus().toggleBold().run()"
      >
        <strong>N</strong>
      </button>
      <button
        type="button"
        :aria-pressed="editor?.isActive('italic')"
        @click="editor?.chain().focus().toggleItalic().run()"
      >
        <em>I</em>
      </button>
      <button
        type="button"
        :aria-pressed="editor?.isActive('heading', { level: 1 })"
        @click="editor?.chain().focus().toggleHeading({ level: 1 }).run()"
      >
        H1
      </button>
      <button
        type="button"
        :aria-pressed="editor?.isActive('heading', { level: 2 })"
        @click="editor?.chain().focus().toggleHeading({ level: 2 }).run()"
      >
        H2
      </button>
      <button
        type="button"
        :aria-pressed="editor?.isActive('heading', { level: 3 })"
        @click="editor?.chain().focus().toggleHeading({ level: 3 }).run()"
      >
        H3
      </button>
      <button
        type="button"
        :aria-pressed="editor?.isActive('bulletList')"
        @click="editor?.chain().focus().toggleBulletList().run()"
      >
        Lista
      </button>
      <button
        type="button"
        :aria-pressed="editor?.isActive('orderedList')"
        @click="editor?.chain().focus().toggleOrderedList().run()"
      >
        Lista numerada
      </button>
      <button type="button" :aria-pressed="editor?.isActive('link')" @click="setLink">
        Link
      </button>
      <button type="button" @click="setImage">Imagem</button>
    </div>

    <EditorContent class="document-viewer__content" :editor="editor" />
  </div>
</template>

<style scoped>
.document-viewer__toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  margin-bottom: 0.5rem;
}

.document-viewer__toolbar button {
  padding: 0.3rem 0.6rem;
  border-radius: 0.375rem;
  border: 1px solid #d1d5db;
  background: white;
  cursor: pointer;
  font-size: 0.85rem;
}

.document-viewer__toolbar button[aria-pressed='true'] {
  background-color: #eef2ff;
  border-color: #6366f1;
}

.document-viewer__content :deep(.tiptap) {
  outline: none;
}

.document-viewer__content :deep(img) {
  max-width: 100%;
  height: auto;
}

.document-viewer__content :deep(code) {
  background-color: #f4f3ec;
  border-radius: 0.25rem;
  padding: 0.1rem 0.3rem;
}
</style>
