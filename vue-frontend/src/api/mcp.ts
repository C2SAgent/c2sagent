import api from './index';
// const api = axios.create({
//   baseURL: import.meta.env.VITE_API_URL
// })

export const McpApi = {
  // 创建MCP服务
  async create(name: string) {
    return await api.post('/manager_mcp/create', name)
  },

  async delete(id: number) {
    return await api.post('/manager_mcp/delete', id)
  },

  // 获取MCP列表
  async list() {
    return await api.get('/manager_mcp/list')
  },

  // 关联工具 (直接接受JSON字符串)
  async correlateTool(mcpId: number, toolJson: string) {
    let body = {
      mcp_server_id: mcpId,
      tool: JSON.parse(toolJson) // 确保是有效的JSON
    }
    return await api.post('/manager_mcp/corr_tool', body)
  },

  async discorrelateTool(mcpId: number, tool_name: string) {
    let body = {
      mcp_server_id: mcpId,
      tool_name: tool_name // 确保是有效的JSON
    }
    return await api.post('/manager_mcp/discorr_tool', body)
  },


  // 获取工具列表 (返回原始JSON)
  async listTools(mcpId: number) {
    return await api.get('/manager_mcp/tool/list', {
        params: { mcp_server_id: mcpId }  // ✅ 标准 GET 传参方式
    }).then(res => res.data.data)
}
}
