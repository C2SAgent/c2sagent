import axios from 'axios'
import type { AgentCard, McpServer } from '@/types'
import api from './index';
// const api = axios.create({
//   baseURL: import.meta.env.VITE_API_BASE_URL
// })

export const AgentApi = {
  // 创建智能体
  async create(agent: AgentCard) {
    return await api.post('/agent/create', agent)
  },
  
  // 获取智能体列表
  async list() {
    return await api.get('/agent/list')
  },
  
  // 删除智能体
  async delete(id: number) {
    return await api.post('/agent/delete',  id);
  },
  
  // 关联MCP服务
  async correlateMcp(agentId: number, mcpId: number) {
    return await api.post('/agent/corr_mcp', {
      agent_card_id: agentId,
      mcp_server_id: mcpId 
    })
  },

  async findMcpByAgent(agentId: number) {
    return await api.get('/agent/find_mcp', {
      params:{
        agent_card_id: agentId,
      }
    })
  },

  async askAgent(question: string){
    return await api.get('/chat/ask-agent', {
      params:{
        question: question,
      }
    })
  }
}