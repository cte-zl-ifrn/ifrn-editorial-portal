<script setup lang="ts">
withDefaults(
  defineProps<{
    kind?: 'info' | 'error'
  }>(),
  { kind: 'info' },
)
</script>

<template>
  <p class="status-message" :class="`status-message--${kind}`" role="alert">
    <slot />
  </p>
</template>

<style scoped>
.status-message {
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  border: 1px solid transparent;
}

.status-message--info {
  background-color: #eef2ff;
  border-color: #c7d2fe;
  color: #3730a3;
}

.status-message--error {
  background-color: #fef2f2;
  border-color: #fecaca;
  color: #991b1b;
}
</style>
