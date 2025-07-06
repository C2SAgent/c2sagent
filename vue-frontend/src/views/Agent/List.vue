<template>
  <div class="agent-list">
    <h2>智能体列表</h2>
    <router-link to="/agent/create" class="create-btn">
      新建智能体
    </router-link>
    <button @click="toggleChat" class="chat-btn">
        {{ showChat ? '隐藏对话' : '与所有智能体对话' }}
    </button>
    <div v-if="showChat" class="simple-chat">
      <div class="chat-area">
        <div v-for="(msg, i) in messages" :key="i" class="message">
          <strong>{{ msg.role === 'user' ? '您' : 'AI' }}:</strong> {{ msg.content }}
        </div>
      </div>
      <div class="chat-input">
        <input
          v-model="inputMessage"
          @keyup.enter="sendMessage"
          placeholder="输入问题..."
        />
        <button @click="sendMessage">发送</button>
      </div>
    </div>
    <div v-if="loading" class="loading">
      <span>加载中...</span>
      <span v-if="loadingProgress">{{ loadingProgress }}</span>
    </div>
    
    <div v-else-if="loadError" class="error-message">
      加载失败: {{ loadError }}
      <button @click="retryLoading">重试</button>
    </div>
    
    <div v-else class="agent-grid">
      <div v-for="agent in agents" :key="agent.id" class="agent-card">
        <h3>{{ agent.name }}</h3>
        <p>{{ agent.description }}</p>
        
        <div class="mcp-info">
          <template v-if="agent.mcp">
            <strong>绑定的MCP:</strong> 
            {{ agent.mcp.name }} (ID: {{ agent.mcp.id }})
            <button @click="unbindMcp(agent.id)" class="unbind-btn">解绑</button>
          </template>
          <template v-else>未绑定MCP</template>
        </div>
        
        <div class="agent-actions">
          <button @click="deleteAgent(agent.id)" class="delete-btn">删除</button>
          <button @click="showMcpSelection(agent)" class="bind-btn">绑定MCP</button>
        </div>
      </div>
    </div>

    <!-- MCP选择弹窗 -->
    <div v-if="showMcpSelect" class="mcp-select-modal">
      <div class="modal-content">
        <h3>为 {{ selectedAgent?.name }} 选择MCP</h3>
        <select v-model="selectedMcpId" class="mcp-select">
          <option value="">请选择MCP</option>
          <option 
            v-for="mcp in mcpList" 
            :key="mcp.id" 
            :value="mcp.id"
            :disabled="selectedAgent?.mcp?.id === mcp.id">
            {{ mcp.name }} (ID: {{ mcp.id }})
          </option>
        </select>
        
        <div class="modal-actions">
          <button @click="confirmBind" :disabled="!selectedMcpId">确认</button>
          <button @click="cancelBind">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { AgentApi } from '@/api/agent'
import { McpApi } from '@/api/mcp'

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
    loadingProgress.value = '加载智能体列表...'
    
    // 加载基础数据
    const [agentsRes, mcpsRes] = await Promise.all([
      AgentApi.list(),
      McpApi.list()
    ])
    
    // 验证数据格式
    if (!agentsRes.data?.data || !mcpsRes.data?.data) {
      throw new Error('API返回数据格式不正确')
    }
    
    agents.value = agentsRes.data.data
    mcpList.value = mcpsRes.data.data
    
    // 加载每个Agent的MCP信息
    loadingProgress.value = '加载MCP绑定信息...'
    for (const agent of agents.value) {
      try {
        const mcpRes = await AgentApi.findMcpByAgent(agent.id)
        agent.mcp = mcpRes.data.data || null
      } catch (error) {
        console.error(`获取Agent ${agent.id}的MCP失败:`, error)
        agent.mcp = null
      }
    }
    
  } catch (error) {
    console.error('加载数据失败:', error)
    loadError.value = error instanceof Error ? error.message : '未知错误'
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
  if (!confirm('确定删除此智能体吗？')) return
  
  try {
    await AgentApi.delete(id)
    agents.value = agents.value.filter(a => a.id !== id)
  } catch (error) {
    alert('删除失败: ' + (error instanceof Error ? error.message : '未知错误'))
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
    
    // 更新本地数据
    const mcp = mcpList.value.find(m => m.id === selectedMcpId.value)
    if (mcp) {
      selectedAgent.value.mcp = mcp
    }
    
    cancelBind()
  } catch (error) {
    alert('绑定失败: ' + (error instanceof Error ? error.message : '未知错误'))
  }
}

const unbindMcp = async (agentId: number) => {
  if (!confirm('确定要解绑此MCP吗？')) return
  
  try {
    await AgentApi.correlateMcp(agentId, 0) // 假设0表示解绑
    
    // 更新本地数据
    const agent = agents.value.find(a => a.id === agentId)
    if (agent) {
      agent.mcp = null
    }
  } catch (error) {
    alert('解绑失败: ' + (error instanceof Error ? error.message : '未知错误'))
  }
}

const showChat = ref(false)
const inputMessage = ref('')
const messages = ref<Array<{
  role: 'user' | 'assistant'
  content: string
}>>([])

// 切换聊天窗口
const toggleChat = () => {
  showChat.value = !showChat.value
  if (showChat.value) {
    messages.value = []
    inputMessage.value = ''
  }
}

// 发送消息
const sendMessage = async () => {
  if (!inputMessage.value.trim()) return

  const userMessage = inputMessage.value
  messages.value.push({ role: 'user', content: userMessage })
  inputMessage.value = ''

  try {
    const res = await AgentApi.askAgent(userMessage)
    
    messages.value.push({
      role: 'assistant',
      content: res.data || '收到空响应'
    })
  } catch (error) {
    messages.value.push({
      role: 'assistant',
      content: '请求出错: ' + (error instanceof Error ? error.message : '未知错误')
    })
  }
}
</script>

<style scoped>
.agent-list {
  padding: 20px;
  position: relative;
  max-width: 1200px;
  margin: 0 auto;
}

.create-btn {
  display: inline-block;
  margin-bottom: 20px;
  padding: 8px 16px;
  background-color: #4CAF50;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.create-btn:hover {
  background-color: #45a049;
}

.loading {
  padding: 20px;
  text-align: center;
  color: #666;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.error-message {
  padding: 20px;
  text-align: center;
  color: #f44336;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.error-message button {
  padding: 8px 16px;
  background-color: #f44336;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 10px;
}

.agent-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.agent-card {
  border: 1px solid #e0e0e0;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  background-color: white;
}

.mcp-info {
  margin: 10px 0;
  padding: 8px;
  background-color: #f8f9fa;
  border-radius: 4px;
  border-left: 3px solid #4285f4;
}

.agent-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.agent-actions button {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.agent-actions button:hover {
  opacity: 0.9;
}

.delete-btn {
  background-color: #f44336;
  color: white;
}

.bind-btn {
  background-color: #4285f4;
  color: white;
}

.unbind-btn {
  margin-left: 10px;
  padding: 2px 6px;
  background-color: #ff9800;
  color: white;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  font-size: 12px;
}

/* MCP选择弹窗样式 */
.mcp-select-modal {
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

.modal-content {
  background-color: white;
  padding: 25px;
  border-radius: 8px;
  width: 450px;
  max-width: 90%;
}

.mcp-select {
  width: 100%;
  padding: 10px;
  margin: 15px 0;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.modal-actions button {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.modal-actions button:first-child {
  background-color: #4CAF50;
  color: white;
}

.modal-actions button:last-child {
  background-color: #f1f1f1;
}

/* 新增的简洁聊天样式 */
.action-buttons {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.chat-btn {
  padding: 8px 16px;
  background-color: #4285f4;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.simple-chat {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
  background-color: #f9f9f9;
}

.chat-area {
  height: 200px;
  overflow-y: auto;
  margin-bottom: 10px;
  padding: 10px;
  background: white;
  border-radius: 4px;
}

.message {
  margin-bottom: 8px;
  line-height: 1.5;
}

.message strong {
  color: #4285f4;
}

.chat-input {
  display: flex;
  gap: 10px;
}

.chat-input input {
  flex: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.chat-input button {
  padding: 8px 16px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

</style>