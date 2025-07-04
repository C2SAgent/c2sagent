import axios from 'axios'
import type { McpServer, Tool } from '@/types'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL
})

export const McpApi = {
  // 创建MCP服务
  create(mcp: Omit<McpServer, 'id'>) {
    return api.post('/mcp/create', mcp)
  },
  
  // 获取MCP列表
  list() {
    return api.get('/mcp/list')
  },
  
  // 关联工具 (直接接受JSON字符串)
  correlateTool(mcpId: string, toolJson: string) {
    return api.post('/mcp/corr_tool', {
      mcp_server: { id: mcpId },
      tool: JSON.parse(toolJson) // 确保是有效的JSON
    })
  },
  
  // 获取工具列表 (返回原始JSON)
  listTools(mcpId: string) {
    return api.post('/mcp/tool/list', {
      mcp_server: { id: mcpId }
    }).then(res => {
      // 直接返回原始数据，不解析
      return res.data.data 
    })
  }
}