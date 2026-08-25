<script setup lang="ts">
import { startLogin } from '../services/authService'
</script>

<template>
  <main class="login">
    <h1>Portal Editorial IFRN</h1>
    <p>Entre com sua conta GitHub para continuar.</p>
    <button type="button" @click="startLogin">Entrar com GitHub</button>
  </main>
</template>

<style scoped>
.login {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 1rem;
  max-width: 32rem;
  margin: 4rem auto;
  text-align: left;
}

button {
  padding: 0.6rem 1.2rem;
  border-radius: 0.5rem;
  border: 1px solid #1f2937;
  background-color: #1f2937;
  color: white;
  cursor: pointer;
}
</style>
