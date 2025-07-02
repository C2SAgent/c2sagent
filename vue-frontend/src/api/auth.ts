import api from './index';
import type { UserCreate, Token, LoginForm, User } from '@/types/auth';

const AuthAPI = {
  async login(formData: LoginForm): Promise<Token> {
    const response = await api.post<Token>('/auth/token', new URLSearchParams({
      username: formData.username,
      password: formData.password,
      grant_type: 'password',
    }), {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  async register(userData: UserCreate): Promise<User> {
    console.log(userData);
    const response = await api.post<UserCreate>('/auth/register', userData);
    return response.data;
  },

  async logout(): Promise<void> {
    return Promise.resolve();
  },

  async refreshToken(refreshToken: string): Promise<Token> {
    const response = await api.post<Token>('/auth/refresh-token', { refresh_token: refreshToken });
    return response.data;
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/auth/users/me');
    return response.data;
  },
};

export default AuthAPI;