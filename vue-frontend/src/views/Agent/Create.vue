<template>
  <div class="agent-create">
    <h2>创建智能体</h2>
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label>名称</label>
        <input v-model="form.name" required>
      </div>
      
      <div class="form-group">
        <label>描述</label>
        <textarea v-model="form.description"></textarea>
      </div>
      
      <div class="form-group">
        <label>LLM名称</label>
        <input v-model="form.llm_name" required>
      </div>
      
      <div class="form-group">
        <label>LLM URL</label>
        <input v-model="form.llm_url">
      </div>
      
      <div class="form-group">
        <label>LLM Key</label>
        <input v-model="form.llm_key" type="password">
      </div>
      
      <div class="form-group">
        <label>版本</label>
        <input v-model="form.version">
      </div>
      
      <div class="form-group">
        <label>
          <input type="checkbox" v-model="form.streaming">
          启用流式响应
        </label>
      </div>
      
      <div class="form-group">
        <label>示例</label>
        <textarea v-model="form.examples" placeholder="['示例1', '示例2']"></textarea>
      </div>
      
      <button type="submit" :disabled="loading">
        {{ loading ? '创建中...' : '创建' }}
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
  examples: []
})

// 监听examples的变化，将文本转换为数组
watch(() => form.value.examples, (newVal) => {
  if (typeof newVal === 'string') {
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