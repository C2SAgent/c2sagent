<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import type { UserCreate } from '@/types/auth';

const router = useRouter();
const authStore = useAuthStore();

const form = ref<UserCreate>({
  name: '',
  password: '',
  core_llm_name: '',
  core_llm_url: '',
  core_llm_key: '',
});

const error = ref('');
const isLoading = ref(false);

async function handleSubmit() {
  try {
    isLoading.value = true;
    error.value = '';
    await authStore.register(form.value);
    router.push('/');
  } catch (err) {
    error.value = 'Registration failed. Username may already be taken.';
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>
  <div class="auth-page">
    <h1>Register</h1>
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label for="username">Username</label>
        <input
          id="username"
          v-model="form.name"
          type="text"
          required
        />
      </div>
      <div class="form-group">
        <label for="password">Password</label>
        <input
          id="password"
          v-model="form.password"
          type="password"
          required
        />
      </div>
      <div class="form-group">
        <label for="core_llm_name">Core LLM Name</label>
        <input
          id="core_llm_name"
          v-model="form.core_llm_name"
          type="text"
        />
      </div>
      <div class="form-group">
        <label for="core_llm_url">Core LLM URL</label>
        <input
          id="core_llm_url"
          v-model="form.core_llm_url"
          type="text"
        />
      </div>
      <div class="form-group">
        <label for="core_llm_key">Core LLM Key</label>
        <input
          id="core_llm_key"
          v-model="form.core_llm_key"
          type="text"
        />
      </div>
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
      <button type="submit" :disabled="isLoading">
        {{ isLoading ? 'Registering...' : 'Register' }}
      </button>
    </form>
    <router-link to="/login">Already have an account? Login</router-link>
  </div>
</template>

<style scoped>
/* 复用Login组件的样式 */
</style>