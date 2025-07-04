<template>
  <div class="tool-management">
    <h2>工具管理 - MCP {{ mcpId }}</h2>
    
    <div class="tool-editor">
      <h3>添加新工具</h3>
      <textarea v-model="newToolJson" placeholder="输入工具JSON格式"></textarea>
      <button @click="addTool" :disabled="!isValidJson">添加工具</button>
      <p v-if="jsonError" class="error">{{ jsonError }}</p>
    </div>
    
    <div class="tool-list">
      <h3>现有工具</h3>
      <div v-for="(tool, index) in tools" :key="index" class="tool-item">
        <pre>{{ JSON.stringify(tool, null, 2) }}</pre>
        <button @click="removeTool(index)">删除</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { McpApi } from '@/api/mcp'

const route = useRoute()
const mcpId = route.params.id as string

const newToolJson = ref('')
const tools = ref<any[]>([])
const jsonError = ref('')

// 检查JSON是否有效
const isValidJson = computed(() => {
  try {
    JSON.parse(newToolJson.value)
    jsonError.value = ''
    return true
  } catch (e) {
    jsonError.value = '无效的JSON格式'
    return false
  }
})

// 加载工具列表
const loadTools = async () => {
  const res = await McpApi.listTools(mcpId)
  tools.value = res
}

// 添加工具
const addTool = async () => {
  try {
    await McpApi.correlateTool(mcpId, newToolJson.value)
    newToolJson.value = ''
    await loadTools()
  } catch (error) {
    alert('添加失败: ' + error.message)
  }
}

// 删除工具
const removeTool = async (index: number) => {
  if (confirm('确定删除此工具吗？')) {
    // 这里需要根据您的后端API实现删除逻辑
    // 假设我们只是从前端列表中移除
    tools.value.splice(index, 1)
  }
}

onMounted(loadTools)
</script>

<style scoped>
.tool-editor textarea {
  width: 100%;
  height: 200px;
  font-family: monospace;
}

.tool-item {
  margin: 1rem 0;
  padding: 1rem;
  border: 1px solid #eee;
}

pre {
  white-space: pre-wrap;
  word-wrap: break-word;
}

.error {
  color: red;
}
</style>