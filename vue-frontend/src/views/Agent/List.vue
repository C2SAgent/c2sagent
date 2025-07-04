<template>
  <div class="agent-list">
    <h2>智能体列表</h2>
    <router-link to="/agent/create" class="create-btn">
      新建智能体
    </router-link>
    
    <div v-if="loading" class="loading">加载中...</div>
    
    <div v-else class="agent-grid">
      <div v-for="agent in agents" :key="agent.id" class="agent-card">
        <h3>{{ agent.name }}</h3>
        <p>{{ agent.description }}</p>
        <button @click="deleteAgent(agent.id)">删除</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { AgentApi } from '@/api/agent'

const loading = ref(true)
const agents = ref<any[]>([])

onMounted(async () => {
  try {
    const res = await AgentApi.list()
    agents.value = res.data.data
  } finally {
    loading.value = false
  }
})

const deleteAgent = async (id: number) => {
  if (confirm('确定删除此智能体吗？')) {
    await AgentApi.delete(id)
    agents.value = agents.value.filter(a => a.id !== id)
  }
}
</script>