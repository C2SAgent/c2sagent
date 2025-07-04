<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const authStore = useAuthStore();

// 确保字段名与后端接口一致（可能是username或name）
const form = ref({
  username: '',  // 如果后端需要name就改为name
  password: '',
});

const error = ref('');
const isLoading = ref(false);

async function handleSubmit() {
  // 调试：先打印表单数据
  console.log('提交的数据:', form.value);

  if (!form.value.username || !form.value.password) {
    error.value = '请填写用户名和密码';
    return;
  }

  try {
    isLoading.value = true;
    error.value = '';
    
    // 方式1：直接传递整个form对象（推荐）
    await authStore.login(form.value);
    
    // 方式2：如果authStore.login需要单独参数
    // await authStore.login(form.value.username, form.value.password);
    
    // 登录成功后跳转
    const redirect = router.currentRoute.value.query.redirect as string;
    router.push(redirect || '/');
  } catch (err) {
    console.error('登录错误:', err);
    error.value = (err as Error).message || '登录失败，请检查用户名和密码';
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>
  <div class="auth-page">
    <h1>登录</h1>
    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label for="username">用户名</label>
        <input
          id="username"
          v-model="form.username"
          type="text"
          required
          autocomplete="username"
          @input="error = ''"
        />
      </div>
      <div class="form-group">
        <label for="password">密码</label>
        <input
          id="password"
          v-model="form.password"
          type="password"
          required
          autocomplete="current-password"
          @input="error = ''"
        />
      </div>
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
      <button type="submit" :disabled="isLoading">
        {{ isLoading ? '登录中...' : '登录' }}
      </button>
    </form>
    <router-link to="/register">没有账号？立即注册</router-link>
  </div>
</template>

<style scoped>
.auth-page {
  max-width: 400px;
  margin: 2rem auto;
  padding: 2rem;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

button {
  width: 100%;
  padding: 0.75rem;
  background-color: #4f46e5;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

button:hover {
  background-color: #4338ca;
}

button:disabled {
  background-color: #c7d2fe;
  cursor: not-allowed;
}

.error-message {
  color: #ef4444;
  margin: 1rem 0;
  text-align: center;
}

a {
  display: block;
  margin-top: 1rem;
  text-align: center;
  color: #4f46e5;
  text-decoration: none;
}
</style>