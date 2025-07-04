<template>
  <div class="mcp-list">
    <h2>MCP服务管理</h2>
    
    <div class="actions">
      <router-link to="/mcp/create" class="btn">
        新建MCP服务
      </router-link>
    </div>
    
    <table v-if="!loading">
      <thead>
        <tr>
          <th>名称</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="mcp in mcps" :key="mcp.id">
          <td>{{ mcp.name }}</td>
          <td>
            <router-link :to="`/mcp/${mcp.id}/tools`">管理工具</router-link>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { McpApi } from '@/api/mcp'

const loading = ref(true)
const mcps = ref<any[]>([])

onMounted(async () => {
  try {
    const res = await McpApi.list()
    mcps.value = res.data.data
  } finally {
    loading.value = false
  }
})
</script>