<script setup lang="ts">
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const authStore = useAuthStore();

onMounted(async () => {
  await authStore.logout();
  router.push('/login');
});
</script>

<template>
  <div class="logout-page">
    <p>Logging out...</p>
  </div>
</template>