import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import AuthAPI from '@/api/auth';
import type { User, UserCreate, Token } from '@/types/auth';
import { useRouter } from 'vue-router';

export const useAuthStore = defineStore('auth', () => {
  const router = useRouter();
  const user = ref<User | null>(null);
  const isAuthenticated = computed(() => !!user.value);

  async function login(username: string, password: string): Promise<void> {
    try {
      const tokens: Token = await AuthAPI.login({ username, password });
      localStorage.setItem('access_token', tokens.access_token);
      localStorage.setItem('refresh_token', tokens.refresh_token);
      
      await fetchUser();
      
      router.push('/');
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  }

  async function register(userData: UserCreate): Promise<void> {
    try {
      await AuthAPI.register(userData);
      await login(userData.name, userData.password);
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  }

  async function logout(): Promise<void> {
    try {
      await AuthAPI.logout();
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      user.value = null;
      router.push('/login');
    } catch (error) {
      console.error('Logout failed:', error);
      throw error;
    }
  }

  async function fetchUser(): Promise<void> {
    try {
      const userData = await AuthAPI.getCurrentUser();
      // 确保不包含密码字段
      const { password, ...userWithoutPassword } = userData as any;
      user.value = userWithoutPassword as User;
    } catch (error) {
      console.error('Failed to fetch user:', error);
      throw error;
    }
  }

  async function init(): Promise<void> {
    const token = localStorage.getItem('access_token');
    if (token && !user.value) {
      try {
        await fetchUser();
      } catch (error) {
        console.error('Initial auth check failed:', error);
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
      }
    }
  }

  return {
    user,
    isAuthenticated,
    login,
    register,
    logout,
    fetchUser,
    init,
  };
});