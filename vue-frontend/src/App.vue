<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'

const authStore = useAuthStore()
const route = useRoute()

// 仅初始化store，不控制渲染逻辑
onMounted(() => {
  authStore.init().catch(err => console.error('初始化失败:', err))
})
</script>

<template>
  <!-- 直接渲染路由视图，不添加额外条件 -->
  <router-view />
</template>