<template>
  <div class="tool-management-container">
    <div class="header-section">
      <h2 class="page-title">{{ t('views.mcp.tool.title') }}: {{ mcpName }}</h2>
    </div>

    <div class="tool-management-content">
      <div class="tool-editor-section">
        <h3 class="section-title">{{ t('views.mcp.tool.addNewTool') }}</h3>

        <div class="form-container">
          <div class="form-group">
            <label for="toolName">{{ t('views.mcp.tool.toolName') }}</label>
            <input id="toolName" v-model="toolForm.name" :placeholder="t('views.mcp.tool.toolNamePlaceholder')" />
          </div>

          <div class="form-group">
            <label for="toolDescription">{{ t('views.mcp.tool.toolDescription') }}</label>
            <textarea
              id="toolDescription"
              v-model="toolForm.description"
              :placeholder="t('views.mcp.tool.toolDescriptionPlaceholder')"
              rows="3"
            ></textarea>
          </div>

          <div class="parameters-section">
            <h4>{{ t('views.mcp.tool.parameterConfig') }}</h4>
            <div v-for="(param, index) in toolForm.parameters" :key="index" class="parameter-item">
              <div class="parameter-header">
                <h5>{{ t('views.mcp.tool.parameter', { index: index + 1 }) }}</h5>
                <button @click="removeParameter(index)" class="small-delete-btn">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                  </svg>
                </button>
              </div>

              <div class="form-group">
                <label :for="`paramName${index}`">{{ t('views.mcp.tool.paramName') }}</label>
                <input :id="`paramName${index}`" v-model="param.name" :placeholder="t('views.mcp.tool.paramNamePlaceholder')" />
              </div>

              <div class="form-group">
                <label :for="`paramType${index}`">{{ t('views.mcp.tool.paramType') }}</label>
                <select :id="`paramType${index}`" v-model="param.type">
                  <option value="string">string</option>
                  <option value="number">number</option>
                  <option value="boolean">boolean</option>
                  <option value="object">object</option>
                  <option value="array">array</option>
                </select>
              </div>

              <div class="checkbox-group">
                <label>
                  <input type="checkbox" v-model="param.required" />
                  {{ t('views.mcp.tool.paramRequired') }}
                </label>
              </div>
            </div>

            <button @click="addParameter" class="add-param-btn">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
              {{ t('views.mcp.tool.addParameter') }}
            </button>
          </div>

          <div class="handler-section">
            <h4>{{ t('views.mcp.tool.handlerConfig') }}</h4>

            <div class="form-group">
              <label for="handlerType">{{ t('views.mcp.tool.handlerType') }}</label>
              <select id="handlerType" v-model="toolForm.handler.type">
                <option value="http_api">HTTP API</option>
              </select>
            </div>

            <div class="form-group">
              <label for="apiUrl">{{ t('views.mcp.tool.apiUrl') }}</label>
              <input id="apiUrl" v-model="toolForm.handler.url" :placeholder="t('views.mcp.tool.apiUrlPlaceholder')" />
            </div>

            <div class="form-group">
              <label for="apiMethod">{{ t('views.mcp.tool.apiMethod') }}</label>
              <select id="apiMethod" v-model="toolForm.handler.method">
                <option value="GET">GET</option>
                <option value="POST">POST</option>
              </select>
            </div>

            <div class="form-group">
              <label for="apiKey">{{ t('views.mcp.tool.apiKey') }}</label>
              <input id="apiKey" v-model="toolForm.handler.key" type="password" :placeholder="t('views.mcp.tool.apiKeyPlaceholder')" />
            </div>
          </div>
        </div>

        <div class="editor-actions">
          <button
            @click="generateJsonAndAddTool"
            :disabled="!isValidForm"
            class="primary-btn"
          >
            {{ t('views.mcp.tool.addTool') }}
          </button>
          <p v-if="jsonError" class="error-message">{{ jsonError }}</p>
        </div>

        <div class="json-preview" v-if="showJsonPreview">
          <h4>{{ t('views.mcp.tool.jsonPreview') }}</h4>
          <pre>{{ generatedJson }}</pre>
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
            <div class="tool-display">
              <h4>{{ tool.name }}</h4>
              <p class="description">{{ tool.description }}</p>

              <div class="tool-details">
                <div class="detail-section">
                  <h5>{{ t('views.mcp.tool.inputParameters') }}</h5>
                  <div v-if="Object.keys(tool.inputSchema.properties).length === 0" class="no-params">
                    {{ t('views.mcp.tool.noParams') }}
                  </div>
                  <div v-else>
                    <div v-for="(prop, propName) in tool.inputSchema.properties" :key="propName" class="param-item">
                      <span class="param-name">{{ propName }}</span>
                      <span class="param-type">{{ prop.type || t('views.mcp.tool.unspecified') }}</span>
                      <span class="param-required" v-if="tool.inputSchema.required.includes(propName)">{{ t('views.mcp.tool.paramRequired') }}</span>
                    </div>
                  </div>
                </div>

                <div class="detail-section">
                  <h5>{{ t('views.mcp.tool.requestConfig') }}</h5>
                  <div class="detail-item">
                    <span class="detail-label">{{ t('views.mcp.tool.type') }}</span>
                    <span class="detail-value">{{ tool.handler.type || t('views.mcp.tool.unspecified') }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">{{ t('views.mcp.tool.url') }}</span>
                    <span class="detail-value">{{ tool.handler.url }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">{{ t('views.mcp.tool.method') }}</span>
                    <span class="detail-value">{{ tool.handler.method || 'GET' }}</span>
                  </div>
                </div>
              </div>
            </div>
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
const mcps = ref<any[]>([])
const loading = ref(true)
const mcpName = ref('')

const toolForm = ref({
  name: '',
  description: '',
  parameters: [
    {
      name: '',
      type: 'string',
      required: true
    }
  ],
  handler: {
    type: 'http_api',
    url: '',
    method: 'GET',
    key: ''
  }
})

const showJsonPreview = ref(false)
const generatedJson = ref('')
const tools = ref<any[]>([])
const jsonError = ref('')

const isValidForm = computed(() => {
  // 检查必填字段
  if (!toolForm.value.name || !toolForm.value.description || !toolForm.value.handler.url) {
    return false
  }

  // 检查所有参数是否有名称
  for (const param of toolForm.value.parameters) {
    if (!param.name) {
      return false
    }
  }

  return true
})

const addParameter = () => {
  toolForm.value.parameters.push({
    name: '',
    type: 'string',
    required: false
  })
}

const removeParameter = (index: number) => {
  if (toolForm.value.parameters.length > 1) {
    toolForm.value.parameters.splice(index, 1)
  }
}

const generateJson = () => {
  const properties: Record<string, any> = {}
  const required: string[] = []

  // 处理参数
  toolForm.value.parameters.forEach(param => {
    if (param.name) {
      properties[param.name] = {
        type: param.type
      }

      if (param.required) {
        required.push(param.name)
      }
    }
  })

  const json = {
    name: toolForm.value.name,
    description: toolForm.value.description,
    inputSchema: {
      type: "object",
      properties,
      required: required.length > 0 ? required : undefined
    },
    handler: {
      type: toolForm.value.handler.type,
      url: toolForm.value.handler.url,
      method: toolForm.value.handler.method,
      key: toolForm.value.handler.key
    }
  }

  // 清理undefined值
  const cleanJson = JSON.parse(JSON.stringify(json))
  return cleanJson
}

const generateJsonAndAddTool = async () => {
  if (!isValidForm.value) {
    jsonError.value = t('views.mcp.tool.formError')
    return
  }

  const json = generateJson()
  generatedJson.value = JSON.stringify(json, null, 2)
  showJsonPreview.value = true

  try {
    await McpApi.correlateTool(Number(mcpId), JSON.stringify(json))
    // 重置表单，保留一个参数
    toolForm.value = {
      name: '',
      description: '',
      parameters: [
        {
          name: '',
          type: 'string',
          required: true
        }
      ],
      handler: {
        type: 'http_api',
        url: '',
        method: 'GET',
        key: ''
      }
    }
    showJsonPreview.value = false
    await loadTools()
  } catch (error) {
    alert(t('errors.addFailed') + ': ' + (error instanceof Error ? error.message : t('errors.unknownError')))
  }
}

const loadTools = async () => {
  const res = await McpApi.listTools(Number(mcpId))
  tools.value = res
}

const removeTool = async (mcpId: number, tool_name: string) => {
  try {
    await McpApi.discorrelateTool(Number(mcpId), tool_name)
    await loadTools()
  } catch (error) {
    alert(t('errors.deleteFailed') + ': ' + (error instanceof Error ? error.message : t('errors.unknownError')))
  }
}

// onMounted()

onMounted(async () => {
  try {
    loadTools()
    const res = await McpApi.list()
    mcps.value = res.data.data
    console.log(mcpId)
    const foundMcp = mcps.value.find(mcp => mcp.id === Number(mcpId));
    mcpName.value = foundMcp?.name || '';
  } finally {
    loading.value = false
  }
})
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

.form-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 500;
  color: #4a5568;
  font-size: 0.875rem;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 0.875rem;
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.parameters-section,
.handler-section {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1rem;
  background-color: white;
}

.parameters-section h4,
.handler-section h4 {
  margin-top: 0;
  margin-bottom: 1rem;
  font-size: 1rem;
  color: #2d3748;
}

.parameter-item {
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 1rem;
  margin-bottom: 1rem;
  background-color: #f8fafc;
  position: relative;
}

.parameter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.parameter-header h5 {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: #4a5568;
}

.small-delete-btn {
  background: none;
  border: none;
  padding: 0.25rem;
  cursor: pointer;
  color: #e53e3e;
}

.small-delete-btn:hover {
  color: #c53030;
}

.checkbox-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.checkbox-group label {
  font-size: 0.875rem;
  color: #4a5568;
}

.add-param-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background-color: #f8fafc;
  color: #4299e1;
  border: 1px dashed #4299e1;
  border-radius: 6px;
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
  width: 100%;
  justify-content: center;
}

.add-param-btn:hover {
  background-color: #ebf8ff;
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

.json-preview {
  margin-top: 1rem;
  padding: 1rem;
  background-color: #f8fafc;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
}

.json-preview h4 {
  margin-top: 0;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
}

.json-preview pre {
  margin: 0;
  font-family: 'Courier New', Courier, monospace;
  font-size: 0.75rem;
  white-space: pre-wrap;
  word-wrap: break-word;
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
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.tool-display {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.tool-display h4 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #2d3748;
}

.description {
  margin: 0;
  font-size: 0.875rem;
  color: #4a5568;
}

.tool-details {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 0.5rem;
}

.detail-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.detail-section h5 {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: #4a5568;
}

.detail-item {
  display: flex;
  gap: 0.5rem;
}

.detail-label {
  font-weight: 500;
  color: #4a5568;
  font-size: 0.875rem;
  min-width: 60px;
}

.detail-value {
  font-size: 0.875rem;
  color: #2d3748;
}

.param-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.25rem 0;
}

.param-name {
  font-weight: 500;
  color: #2d3748;
  font-size: 0.875rem;
  min-width: 100px;
}

.param-type {
  font-size: 0.75rem;
  color: #718096;
  background-color: #f8fafc;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.param-required {
  font-size: 0.75rem;
  color: #e53e3e;
  background-color: #fff5f5;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.no-params {
  font-size: 0.875rem;
  color: #718096;
  font-style: italic;
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
  align-self: flex-end;
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
