<template>
  <div class="agent-list-container">
    <div class="header-section">
      <h2 class="page-title">{{ t('views.agent.list.title') }}</h2>
      <div class="action-buttons">
        <router-link to="/agent/create" class="primary-btn">
          <span>+</span> {{ t('views.agent.list.newAgent') }}
        </router-link>
        <router-link to="/" class="secondary-btn">
          {{ t('views.agent.list.chatWithTeam') }}
        </router-link>
        <router-link to="/mcp/create" class="primary-btn">
          <span>⚙️</span> {{ t('components.sidebar.manageMcp') }}
        </router-link>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <span>{{ t('views.agent.list.loadingAgents') }}</span>
      <span v-if="loadingProgress" class="progress-text">{{ loadingProgress }}</span>
    </div>

    <div v-else-if="loadError" class="error-state">
      <div class="error-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
      </div>
      <div class="error-message">{{ t('views.agent.list.loadFailed') }}: {{ loadError }}</div>
      <button @click="retryLoading" class="retry-btn">{{ t('common.retry') }}</button>
    </div>

    <div v-else class="agent-grid">
      <div v-for="agent in agents" :key="agent.id" class="agent-card">
        <div class="card-header">
          <h3 class="agent-name">{{ agent.name }}</h3>
          <div class="agent-version">v{{ agent.version || '1.0' }}</div>
        </div>
        <p class="agent-description">{{ agent.description || t('views.agent.list.noDescription') }}</p>

        <div class="mcp-info" :class="{ 'unbound': !agent.mcp }">
          <template v-if="agent.mcp">
            <div class="mcp-name">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M18 8h1a4 4 0 0 1 0 8h-1"></path>
                <path d="M12 8h1a4 4 0 0 1 0 8h-1"></path>
                <path d="M6 8H7a4 4 0 0 1 0 8H6"></path>
              </svg>
              <span>{{ agent.mcp.name }}</span>
            </div>
            <div class="mcp-id">{{ t('views.agent.list.mcpId') }}: {{ agent.mcp.id }}</div>
            <button @click="unbindMcp(agent.id, agent.mcp.id)" class="unbind-btn">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
              {{ t('views.agent.list.unbindMcp') }}
            </button>
          </template>
          <template v-else>
            <div class="unbound-text">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
              <span>{{ t('views.agent.list.unboundMcp') }}</span>
            </div>
          </template>
        </div>

        <div class="card-actions">
          <button @click="deleteAgent(agent.id)" class="delete-btn">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="3 6 5 6 21 6"></polyline>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
              <line x1="10" y1="11" x2="10" y2="17"></line>
              <line x1="14" y1="11" x2="14" y2="17"></line>
            </svg>
            {{ t('common.delete') }}
          </button>
          <button @click="showMcpSelection(agent)" class="bind-btn">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M18 8h1a4 4 0 0 1 0 8h-1"></path>
              <path d="M12 8h1a4 4 0 0 1 0 8h-1"></path>
              <path d="M6 8H7a4 4 0 0 1 0 8H6"></path>
            </svg>
            {{ t('views.agent.list.bindMcp') }}
          </button>
        </div>
      </div>
    </div>

    <!-- MCP选择弹窗 -->
    <div v-if="showMcpSelect" class="modal-overlay">
      <div class="modal-container">
        <div class="modal-header">
          <h3>{{ t('views.agent.list.selectMcpFor') }} {{ selectedAgent?.name }}</h3>
          <button @click="cancelBind" class="modal-close-btn">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <select v-model="selectedMcpId" class="modal-select">
            <option value="">{{ t('views.agent.list.selectMcp') }}</option>
            <option
              v-for="mcp in mcpList"
              :key="mcp.id"
              :value="mcp.id"
              :disabled="selectedAgent?.mcp?.id === mcp.id">
              {{ mcp.name }} ({{ t('views.agent.list.mcpId') }}: {{ mcp.id }})
            </option>
          </select>
        </div>
        <div class="modal-footer">
          <router-link to="/mcp/create" class="primary-btn">
            <span>+</span> {{ t('views.mcp.list.newMcp') }}
          </router-link>
          <button @click="cancelBind" class="modal-cancel-btn">{{ t('common.cancel') }}</button>
          <button @click="confirmBind" :disabled="!selectedMcpId" class="modal-confirm-btn">{{ t('views.agent.list.confirmBind') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { AgentApi } from '@/api/agent'
import { McpApi } from '@/api/mcp'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

// 状态管理
const loading = ref(true)
const loadingProgress = ref('')
const loadError = ref('')
const agents = ref<any[]>([])
const mcpList = ref<any[]>([])
const showMcpSelect = ref(false)
const selectedAgent = ref<any>(null)
const selectedMcpId = ref<number | null>(null)

// 加载数据
const loadData = async () => {
  try {
    loading.value = true
    loadError.value = ''
    loadingProgress.value = t('views.agent.list.loadingAgentList')

    const [agentsRes, mcpsRes] = await Promise.all([
      AgentApi.list(),
      McpApi.list()
    ])

    if (!agentsRes.data?.data || !mcpsRes.data?.data) {
      throw new Error(t('errors.invalidApiResponse'))
    }

    agents.value = agentsRes.data.data
    mcpList.value = mcpsRes.data.data

    loadingProgress.value = t('views.agent.list.loadingMcpInfo')
    for (const agent of agents.value) {
      try {
        const mcpRes = await AgentApi.findMcpByAgent(agent.id)
        agent.mcp = mcpRes.data.data || null
      } catch (error) {
        console.error(t('errors.getAgentMcpFailed', { id: agent.id }), error)
        agent.mcp = null
      }
    }

  } catch (error) {
    console.error(t('errors.loadDataFailed'), error)
    loadError.value = error instanceof Error ? error.message : t('errors.unknownError')
  } finally {
    loading.value = false
    loadingProgress.value = ''
  }
}

// 初始化加载
onMounted(loadData)

// 重试加载
const retryLoading = () => {
  loadData()
}

// 删除智能体
const deleteAgent = async (id: number) => {
  if (!confirm(t('views.agent.list.confirmDelete'))) return

  try {
    await AgentApi.delete(id)
    agents.value = agents.value.filter(a => a.id !== id)
  } catch (error) {
    alert(t('errors.deleteFailed')+ ": " + t('errors.discorrMCP'))// + (error instanceof Error ? error.message : t('errors.unknownError')))
  }
}

// MCP绑定相关
const showMcpSelection = (agent: any) => {
  selectedAgent.value = agent
  selectedMcpId.value = agent.mcp?.id || null
  showMcpSelect.value = true
}

const cancelBind = () => {
  showMcpSelect.value = false
  selectedAgent.value = null
  selectedMcpId.value = null
}

const confirmBind = async () => {
  if (!selectedAgent.value || !selectedMcpId.value) return

  try {
    await AgentApi.correlateMcp(selectedAgent.value.id, selectedMcpId.value)

    const mcp = mcpList.value.find(m => m.id === selectedMcpId.value)
    if (mcp) {
      selectedAgent.value.mcp = mcp
    }

    cancelBind()
  } catch (error) {
    alert(t('errors.bindFailed') + ': ' + (error instanceof Error ? error.message : t('errors.unknownError')))
  }
}

const unbindMcp = async (agentId: number, mcpId: number) => {
  if (!confirm(t('views.agent.list.confirmUnbind'))) return

  try {
    await AgentApi.discorrelateMcp(agentId, mcpId)

    const agent = agents.value.find(a => a.id === agentId)
    if (agent) {
      agent.mcp = null
    }
  } catch (error) {
    alert(t('errors.unbindFailed') + ': ' + (error instanceof Error ? error.message : t('errors.unknownError')))
  }
}
</script>

<style scoped>
.agent-list-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
}

.action-buttons {
  display: flex;
  gap: 0.75rem;
}

.primary-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background-color: #4299e1;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
  text-decoration: none;
}

.primary-btn:hover {
  background-color: #3182ce;
}

.secondary-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background-color: white;
  color: #4299e1;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
  text-decoration: none;
}

.secondary-btn:hover {
  background-color: #f8fafc;
  border-color: #cbd5e0;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  gap: 1rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(66, 153, 225, 0.2);
  border-radius: 50%;
  border-top-color: #4299e1;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.progress-text {
  color: #718096;
  font-size: 0.875rem;
}

.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  gap: 1rem;
}

.error-icon {
  color: #e53e3e;
}

.error-message {
  color: #e53e3e;
  font-weight: 500;
}

.retry-btn {
  padding: 0.75rem 1.25rem;
  background-color: #e53e3e;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.retry-btn:hover {
  background-color: #c53030;
}

.agent-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.25rem;
  margin-top: 1.5rem;
}

.agent-card {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 1.25rem;
  background-color: white;
  transition: all 0.2s;
}

.agent-card:hover {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.agent-name {
  font-size: 1.125rem;
  font-weight: 600;
  color: #2d3748;
  margin: 0;
}

.agent-version {
  font-size: 0.75rem;
  color: #718096;
  background-color: #f8fafc;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.agent-description {
  color: #4a5568;
  font-size: 0.875rem;
  margin-bottom: 1rem;
  line-height: 1.5;
}

.mcp-info {
  padding: 0.75rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  background-color: #f8fafc;
  border-left: 4px solid #4299e1;
}

.mcp-info.unbound {
  border-left-color: #e2e8f0;
}

.mcp-name {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
  color: #2d3748;
  margin-bottom: 0.25rem;
}

.mcp-id {
  font-size: 0.75rem;
  color: #718096;
}

.unbound-text {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #718096;
}

.unbind-btn {
  margin-top: 0.5rem;
  padding: 0.25rem 0.5rem;
  background-color: transparent;
  color: #e53e3e;
  border: 1px solid #e53e3e;
  border-radius: 4px;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.unbind-btn:hover {
  background-color: rgba(229, 62, 62, 0.1);
}

.card-actions {
  display: flex;
  gap: 0.75rem;
}

.delete-btn {
  flex: 1;
  padding: 0.5rem;
  background-color: white;
  color: #e53e3e;
  border: 1px solid #e53e3e;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.delete-btn:hover {
  background-color: rgba(229, 62, 62, 0.1);
}

.bind-btn {
  flex: 1;
  padding: 0.5rem;
  background-color: white;
  color: #4299e1;
  border: 1px solid #4299e1;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.bind-btn:hover {
  background-color: rgba(66, 153, 225, 0.1);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-container {
  background-color: white;
  border-radius: 12px;
  width: 450px;
  max-width: 90%;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
}

.modal-close-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: #718096;
  padding: 0.25rem;
  border-radius: 4px;
}

.modal-close-btn:hover {
  background-color: #f8fafc;
}

.modal-body {
  padding: 1.5rem;
}

.modal-select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.modal-select:focus {
  outline: none;
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.2);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #e2e8f0;
}

.modal-cancel-btn {
  padding: 0.75rem 1.25rem;
  background-color: white;
  color: #4a5568;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.modal-cancel-btn:hover {
  background-color: #f8fafc;
}

.modal-confirm-btn {
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

.modal-confirm-btn:hover {
  background-color: #3182ce;
}

.modal-confirm-btn:disabled {
  background-color: #a0aec0;
  cursor: not-allowed;
}
</style>
