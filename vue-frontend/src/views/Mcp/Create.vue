<template>
  <div class="mcp-create">
    <h2>创建MCP</h2>
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label>名称</label>
        <input v-model="form.name" required>
      </div>
      
      <button type="submit" :disabled="loading">
        {{ loading ? '创建中...' : '创建' }}
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { McpApi } from '@/api/mcp'
import { useRouter } from 'vue-router'

const router = useRouter()
const loading = ref(false)

const form = ref({
  name: '',
})

const handleSubmit = async () => {
  try {
    loading.value = true
    await McpApi.create(form.value.name)
    router.push('/mcp/list')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.mcp-create {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
}
.form-group {
  margin-bottom: 15px;
}
label {
  display: block;
  margin-bottom: 5px;
}
input[type="text"],
input[type="password"],
textarea {
  width: 100%;
  padding: 8px;
  box-sizing: border-box;
}
textarea {
  height: 100px;
}
button {
  padding: 10px 15px;
  background-color: #4CAF50;
  color: white;
  border: none;
  cursor: pointer;
}
button:disabled {
  background-color: #cccccc;
}
</style>