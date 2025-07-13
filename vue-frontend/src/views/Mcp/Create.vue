<template>
  <div class="mcp-create-container">
    <h2 class="page-title">创建MCP服务</h2>
    <form @submit.prevent="handleSubmit" class="modern-form">
      <div class="form-group">
        <label class="form-label">名称</label>
        <input 
          v-model="form.name" 
          required
          class="form-input"
          placeholder="输入MCP服务名称"
        >
      </div>
      
      <button type="submit" :disabled="loading" class="submit-btn">
        {{ loading ? '创建中...' : '创建MCP服务' }}
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
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
.mcp-create-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 2rem;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.page-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 1.5rem;
  text-align: center;
}

.modern-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #4a5568;
}

.form-input {
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.2);
}

.submit-btn {
  padding: 0.75rem 1.5rem;
  background-color: #4299e1;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
  margin-top: 0.5rem;
}

.submit-btn:hover {
  background-color: #3182ce;
}

.submit-btn:disabled {
  background-color: #a0aec0;
  cursor: not-allowed;
}

.submit-btn:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.3);
}
</style>