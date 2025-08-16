<template>
  <div class="agent-create">
    <h2 class="page-title">创建智能体</h2>
    <form @submit.prevent="handleSubmit" class="modern-form">
      <div class="form-group">
        <label class="form-label">名称</label>
        <input v-model="form.name" required class="form-input">
      </div>
      
      <div class="form-group">
        <label class="form-label">描述</label>
        <textarea v-model="form.description" class="form-textarea"></textarea>
      </div>
      
      <div class="form-group">
        <label class="form-label">LLM名称</label>
        <input v-model="form.llm_name" required class="form-input">
      </div>
      
      <div class="form-group">
        <label class="form-label">LLM URL</label>
        <input v-model="form.llm_url" class="form-input">
      </div>
      
      <div class="form-group">
        <label class="form-label">LLM Key</label>
        <input v-model="form.llm_key" type="password" class="form-input">
      </div>
      
      <div class="form-group">
        <label class="form-label">版本</label>
        <input v-model="form.version" class="form-input">
      </div>
      
      <div class="form-group checkbox-group">
        <label class="checkbox-label">
          <input type="checkbox" v-model="form.streaming" class="checkbox-input">
          <span class="checkbox-custom"></span>
          启用流式响应
        </label>
      </div>
      
      <div class="form-group">
        <label class="form-label">示例</label>
        <textarea v-model="form.examples" placeholder="['示例1', '示例2']" class="form-textarea"></textarea>
      </div>
      
      <button type="submit" :disabled="loading" class="submit-btn">
        {{ loading ? '创建中...' : '创建智能体' }}
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { AgentApi } from '@/api/agent'
import { useRouter } from 'vue-router'

const router = useRouter()
const loading = ref(false)

const form = ref({
  name: '',
  description: '',
  llm_name: 'gpt-4',
  llm_url: '',
  llm_key: '',
  version: '1.0',
  streaming: false,
  examples: ['']
})

// 监听examples的变化，将文本转换为数组
watch(() => form.value.examples, (newVal: string | string[]) => {
  if (typeof newVal === 'string') {
    // 确保赋值的类型匹配
    form.value.examples = newVal.split('\n').filter(line => line.trim())
  }
}, { deep: true })

const handleSubmit = async () => {
  try {
    loading.value = true
    await AgentApi.create(form.value)
    router.push('/agent/list')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.agent-create {
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

.form-textarea {
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.875rem;
  min-height: 100px;
  resize: vertical;
  transition: all 0.2s;
}

.form-textarea:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.2);
}

.checkbox-group {
  margin-top: 0.5rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  user-select: none;
  color: #4a5568;
}

.checkbox-input {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

.checkbox-custom {
  position: relative;
  height: 1.25rem;
  width: 1.25rem;
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  transition: all 0.2s;
}

.checkbox-input:checked ~ .checkbox-custom {
  background-color: #4299e1;
  border-color: #4299e1;
}

.checkbox-custom:after {
  content: "";
  position: absolute;
  display: none;
  left: 7px;
  top: 3px;
  width: 5px;
  height: 10px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.checkbox-input:checked ~ .checkbox-custom:after {
  display: block;
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