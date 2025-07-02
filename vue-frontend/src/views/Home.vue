<script setup lang="ts">
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
</script>

<template>
  <div class="home-page">
    <h1>Welcome, {{ authStore.user?.name }}!</h1>
    <div v-if="authStore.user">
      <p>Core LLM: {{ authStore.user.core_llm_name || 'Not set' }}</p>
      <p>LLM URL: {{ authStore.user.core_llm_url || 'Not set' }}</p>
    </div>
    <router-link to="/logout" class="logout-link">Logout</router-link>
  </div>
</template>

<style scoped>
.home-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  text-align: center;
}

.logout-link {
  display: inline-block;
  margin-top: 2rem;
  color: #42b983;
  text-decoration: none;
}

.logout-link:hover {
  text-decoration: underline;
}
</style>