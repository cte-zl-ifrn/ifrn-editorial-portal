<script setup lang="ts">
import { watch } from 'vue'
import { EditorContent, useEditor } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Image from '@tiptap/extension-image'
import { markdownToTiptap } from '../lib/markdownToTiptap'

/**
 * Renderiza Markdown em modo somente leitura via Tiptap (Fase 2.1) —
 * ver docs/phase-2.1-plan.md. Edição (Fase 2.2) habilita `editable: true`
 * e adiciona o serializer de volta para Markdown.
 */
const props = defineProps<{
  markdown: string
}>()

const editor = useEditor({
  content: markdownToTiptap(props.markdown),
  editable: false,
  extensions: [
    StarterKit.configure({
      link: { openOnClick: false, autolink: false },
    }),
    Image,
  ],
})

watch(
  () => props.markdown,
  (markdown) => {
    editor.value?.commands.setContent(markdownToTiptap(markdown))
  },
)
</script>

<template>
  <EditorContent class="document-viewer" :editor="editor" />
</template>

<style scoped>
.document-viewer :deep(.tiptap) {
  outline: none;
}

.document-viewer :deep(img) {
  max-width: 100%;
  height: auto;
}

.document-viewer :deep(code) {
  background-color: #f4f3ec;
  border-radius: 0.25rem;
  padding: 0.1rem 0.3rem;
}
</style>
