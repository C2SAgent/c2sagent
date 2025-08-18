<template>
  <div class="tool-management-container">
    <div class="header-section">
      <h2 class="page-title">{{ t('views.mcp.tool.title', { id: mcpId }) }}</h2>
    </div>

    <div class="tool-management-content">
      <div class="tool-editor-section">
        <h3 class="section-title">{{ t('views.mcp.tool.addNewTool') }}</h3>
        <textarea
          v-model="newToolJson"
          :placeholder="t('views.mcp.tool.jsonPlaceholder')"
          class="json-textarea"
        ></textarea>
        <div class="editor-actions">
          <button
            @click="addTool"
            :disabled="!isValidJson"
            class="primary-btn"
          >
            {{ t('views.mcp.tool.addTool') }}
          </button>
          <p v-if="jsonError" class="error-message">{{ jsonError }}</p>
        </div>
      </div>

      <div class="tool-list-section">
        <h3 class="section-title">{{ t('views.mcp.tool.existingTools') }}</h3>
        <div v-if="tools.length === 0" class="empty-state">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          <span>{{ t('views.mcp.tool.noTools') }}</span>
        </div>
        <div v-else>
          <div
            v-for="(tool, index) in tools"
            :key="index"
            class="tool-item"
          >
            <pre class="tool-json">{{ JSON.stringify(tool, null, 2) }}</pre>
            <button
              @click="removeTool(Number(mcpId), tool.name)"
              class="delete-btn"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="3 6 5 6 21 6"></polyline>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                <line x1="10" y1="11" x2="10" y2="17"></line>
                <line x1="14" y1="11" x2="14" y2="17"></line>
              </svg>
              {{ t('common.delete') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { McpApi } from '@/api/mcp'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const route = useRoute()
const mcpId = route.params.id

const newToolJson = ref('')
const tools = ref<any[]>([])
const jsonError = ref('')

const isValidJson = computed(() => {
  try {
    JSON.parse(newToolJson.value)
    jsonError.value = ''
    return true
  } catch (e) {
    jsonError.value = t('errors.invalidJson')
    return false
  }
})

const loadTools = async () => {
  const res = await McpApi.listTools(Number(mcpId))
  tools.value = res
}

const addTool = async () => {
  try {
    await McpApi.correlateTool(Number(mcpId), newToolJson.value)
    newToolJson.value = ''
    await loadTools()
  } catch (error) {
    alert(t('errors.addFailed') + ': ' + (error instanceof Error ? error.message : t('errors.unknownError')))
  }
}

const removeTool = async (mcpId: number, tool_name: string) => {
  try {
    await McpApi.discorrelateTool(Number(mcpId), tool_name)
    newToolJson.value = ''
    await loadTools()
  } catch (error) {
    alert(t('errors.deleteFailed') + ': ' + (error instanceof Error ? error.message : t('errors.unknownError')))
  }
}

onMounted(loadTools)
</script>

<style scoped>
.tool-management-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.header-section {
  margin-bottom: 1.5rem;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
}

.tool-management-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.tool-editor-section,
.tool-list-section {
  background-color: #f8fafc;
  border-radius: 12px;
  padding: 1.5rem;
}

.section-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #4a5568;
  margin-bottom: 1rem;
}

.json-textarea {
  width: 100%;
  height: 300px;
  padding: 1rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-family: 'Courier New', Courier, monospace;
  font-size: 0.875rem;
  line-height: 1.5;
  resize: vertical;
  transition: all 0.2s;
}

.json-textarea:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.2);
}

.editor-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-top: 1rem;
}

.primary-btn {
  padding: 0.75rem 1.25rem;
  background-color: #4299e1;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.primary-btn:hover {
  background-color: #3182ce;
}

.primary-btn:disabled {
  background-color: #a0aec0;
  cursor: not-allowed;
}

.error-message {
  color: #e53e3e;
  font-size: 0.875rem;
  margin: 0;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  gap: 1rem;
  color: #718096;
}

.empty-state svg {
  color: #cbd5e0;
}

.tool-item {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
  background-color: white;
}

.tool-json {
  background-color: #f8fafc;
  padding: 1rem;
  border-radius: 6px;
  font-family: 'Courier New', Courier, monospace;
  font-size: 0.875rem;
  line-height: 1.5;
  white-space: pre-wrap;
  word-wrap: break-word;
  margin-bottom: 1rem;
}

.delete-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background-color: white;
  color: #e53e3e;
  border: 1px solid #e53e3e;
  border-radius: 6px;
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.delete-btn:hover {
  background-color: rgba(229, 62, 62, 0.1);
}

@media (max-width: 768px) {
  .tool-management-content {
    grid-template-columns: 1fr;
  }
}
</style>
