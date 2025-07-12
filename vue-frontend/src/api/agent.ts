import axios from 'axios'
import type { AgentCard, McpServer } from '@/types'
import api from './index';
// const api = axios.create({
//   baseURL: import.meta.env.VITE_API_BASE_URL
// })

export const AgentApi = {
  // 创建智能体
  async create(agent: AgentCard) {
    return await api.post('/manager_agent/create', agent)
  },
  
  // 获取智能体列表
  async list() {
    return await api.get('/manager_agent/list')
  },
  
  // 删除智能体
  async delete(id: number) {
    return await api.post('/manager_agent/delete',  id);
  },
  
  // 关联MCP服务
  async correlateMcp(agentId: number, mcpId: number) {
    return await api.post('/manager_agent/corr_mcp', {
      agent_card_id: agentId,
      mcp_server_id: mcpId 
    })
  },

  async findMcpByAgent(agentId: number) {
    return await api.get('/manager_agent/find_mcp', {
      params:{
        agent_card_id: agentId,
      }
    })
  },

  async askAgent(session_id: string, question: string): Promise<string>{
    let response = await api.get('/app_a2a/ask_a2a', {
      params:{
        session_id: session_id,
        question: question,
      }
    })
    let result: string = response.data.data
    return result
  }
}