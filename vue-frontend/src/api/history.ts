import type { ChatMessage, ChatSession } from '@/types/chat';
import api from './index';

export const HistoryApi = {
  // 创建智能体
  async create() {
    let response = await api.post('/app_history/create')
    let result: ChatSession = response.data.data
    return result
  },
  
  // 获取智能体列表
  async list(): Promise<ChatSession[]> {
    let response = await api.get('/app_history/list')
    let result: ChatSession[] = response.data.data
    console.log(result)
    return result
  },

  async load(session_id: string): Promise<ChatSession>{
    let response = await api.get('/app_history/load', {
      params:{
        session_id: session_id,
      }
    })
    let result: ChatSession = response.data.data
    return result
  },

  async delete(session_id: string) {
    await api.post('/app_history/delete', session_id=session_id)
  },
}