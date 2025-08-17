import type { AxiosProgressEvent } from 'axios';
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

  async discorrelateMcp(agentId: number, mcpId: number) {
    return await api.post('/manager_agent/discorr_mcp', {
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
  },

  async askAgentStreaming(
    session_id: string,
    question: string,
    isTimeSeries: boolean,
    isAgent: boolean,
    isThought: boolean,
    file?: File
  ): Promise<ReadableStream> {
    const formData = new FormData();
    if(file){
      formData.append("files", file);
    }
    formData.append("question", question);
    formData.append("session_id", session_id);
    formData.append("isTimeSeries", String(isTimeSeries));
    formData.append("isAgent", String(isAgent));
    formData.append("isThought", String(isThought));
    formData.append("isDocAnalysis", "false");
    const token = localStorage.getItem('access_token');
    // console.log(token)
    const response = await fetch('https://api.c2sagent.com/app_a2a/ask_a2a_streaming', {
      method: 'POST',
      body: formData,
      headers: {
        // 'Content-Type': 'multipart/form-data',
        'Authorization': `Bearer ${token}`
      },
      // 不需要手动设置 Content-Type，FormData 会自动设置
    });

    if (!response.ok) {
      throw new Error(`请求失败: ${response.status}`);
    }

    if (!response.body) {
      throw new Error('响应体为空');
    }

    return response.body;
  }

// async askAgentStreaming(
//   session_id: string,
//   question: string,
//   isTimeSeries: boolean,
//   file?: File
// ): Promise<ReadableStream> {  // 明确返回 ReadableStream
//   console.log("调用streaming接口");
//   const formData = new FormData();
//   if(file){
//     formData.append("files", file);
//   }
//   formData.append("question", question);
//   formData.append("session_id", session_id);
//   formData.append("isTimeSeries", String(isTimeSeries));
//   formData.append("isDocAnalysis", "false");

//   const response = await api.post('/app_a2a/ask_a2a_streaming', formData, {
//     headers: {
//       'Content-Type': 'multipart/form-data',
//     },
//     responseType: 'stream' // 确保请求返回流
//   });

//   // 确保返回的是 ReadableStream
//   if (response.data instanceof ReadableStream) {
//     return response.data;
//   }
//   throw new Error('响应不是有效的ReadableStream');
// }
}
