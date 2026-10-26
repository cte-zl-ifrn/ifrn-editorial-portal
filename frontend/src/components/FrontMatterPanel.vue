<script setup lang="ts">
defineProps<{
  frontMatter: Record<string, unknown>
}>()

function formatValue(value: unknown): string {
  if (Array.isArray(value)) return value.map(String).join(', ')
  if (value === null || value === undefined) return ''
  return String(value)
}
</script>

<template>
  <section class="front-matter" aria-labelledby="front-matter-heading">
    <h2 id="front-matter-heading">Metadados</h2>
    <p v-if="Object.keys(frontMatter).length === 0" class="front-matter__empty">
      Este documento não possui front matter.
    </p>
    <dl v-else class="front-matter__list">
      <template v-for="(value, key) in frontMatter" :key="key">
        <dt>{{ key }}</dt>
        <dd>{{ formatValue(value) }}</dd>
      </template>
    </dl>
  </section>
</template>

<style scoped>
.front-matter {
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1rem;
}

.front-matter__list {
  display: grid;
  grid-template-columns: max-content 1fr;
  gap: 0.25rem 1rem;
  margin: 0;
}

.front-matter__list dt {
  font-weight: 600;
  color: #6b7280;
}

.front-matter__list dd {
  margin: 0;
}

.front-matter__empty {
  color: #6b7280;
}
</style>
