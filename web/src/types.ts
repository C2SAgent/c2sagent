// 用户相关类型
export interface User {
  id: number;
  name: string;
  core_llm_name?: string;
  core_llm_url?: string;
  core_llm_key?: string;
}

// API 响应类型
export interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  status: number;
}

// Token 相关类型
export interface TokenData {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface TokenPayload {
  sub: string;
  exp: number;
  last_activity: number;
}




export interface AgentCard {
  id?: number
  name: string
  description?: string
  llm_name: string
  llm_url?: string
  llm_key?: string
  version?: string
  streaming?: boolean
  examples?: any[]
}

export interface McpServer {
  id?: number
  name: string
}

export interface Tool {
  id?: string
  name: string
  url: string
}