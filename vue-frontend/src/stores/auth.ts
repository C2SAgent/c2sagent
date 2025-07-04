import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import AuthAPI from '@/api/auth';
import type { User, UserCreate, Token, LoginForm } from '@/types/auth'; // 确保导入LoginForm类型
import { useRouter } from 'vue-router';

export const useAuthStore = defineStore('auth', () => {
  const router = useRouter();
  const user = ref<User | null>(null);
  const _isInitialized = ref(false); // 内部状态
  
  // 暴露为计算属性确保响应性
  const isInitialized = computed(() => _isInitialized.value);
  const isAuthenticated = computed(() => !!user.value);

  // 清理认证信息
  const clearAuth = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    user.value = null;
  };

  // 登录方法（严格类型校验）
  const login = async (formData: LoginForm): Promise<void> => {
    try {
      const tokens = await AuthAPI.login({
        username: formData.username,
        password: formData.password
      });
      
      localStorage.setItem('access_token', tokens.access_token);
      localStorage.setItem('refresh_token', tokens.refresh_token);
      
      await fetchUser();
      router.push('/');
    } catch (error) {
      clearAuth();
      throw new Error('登录失败: ' + (error as Error).message);
    }
  };

  // 获取用户信息
  const fetchUser = async (): Promise<void> => {
    try {
      const userData = await AuthAPI.getCurrentUser();
      // 类型安全过滤敏感字段
      user.value = {
        id: userData.id,
        name: userData.name,
        core_llm_name: userData.core_llm_name,
        core_llm_url: userData.core_llm_url
      } as User;
    } catch (error) {
      clearAuth();
      throw error;
    }
  };

  // 初始化方法（关键修复点）
  const init = async (): Promise<void> => {
    try {
      const token = localStorage.getItem('access_token');
      if (token) await fetchUser();
    } catch (error) {
      console.error('初始化失败:', error);
    } finally {
      _isInitialized.value = true; // 确保最终标记初始化完成
    }
  };

  // 暴露的成员必须明确类型
  return {
    user: computed(() => user.value),
    isAuthenticated,
    isInitialized,
    login,
    register: async (userData: UserCreate) => {
      await AuthAPI.register(userData);
      await login({ 
        username: userData.name, 
        password: userData.password 
      });
    },
    logout: async () => {
      await AuthAPI.logout();
      clearAuth();
      router.push('/login');
    },
    init
  };
});