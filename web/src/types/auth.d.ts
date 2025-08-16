export interface UserBase {
  name: string;
  core_llm_name?: string;
  core_llm_url?: string;
  core_llm_key?: string;
}

export interface User extends UserBase {
  id?: number;
  // 其他用户属性，但不包含密码
}

export interface UserCreate extends UserBase {
  password: string;
}

export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginForm {
  username: string;
  password: string;
}