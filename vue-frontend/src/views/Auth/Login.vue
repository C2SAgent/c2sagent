<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const authStore = useAuthStore();

const form = ref({
  username: '',
  password: '',
});

const error = ref('');
const isLoading = ref(false);

// 新增一键填充函数
const fillDemoCredentials = () => {
  form.value.username = 'agent';
  form.value.password = 'agent';
  error.value = '';
};

async function handleSubmit() {
  if (!form.value.username || !form.value.password) {
    error.value = '请填写用户名和密码';
    return;
  }

  try {
    isLoading.value = true;
    error.value = '';
    await authStore.login(form.value);
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
  <div class="page-container">
    <div class="auth-page">
      <h2 style="display: flex; align-items: center; gap: 8px">
        <img src="../../assets/logo.png" alt="logo" class="logo" />
        <span>C2S Agent</span>
      </h2>
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
      <div class="demo-account">
        <p style="
          margin: 0rem 0;
          display: flex;
          align-items: baseline; /* 关键修改 */
          justify-content: center;
          gap: 8px;
        ">
          <span>体验账号: agent | 体验密码: agent</span>
          <a
            @click.prevent="fillDemoCredentials"
            style="
              cursor: pointer;
              color: #4f46e5;
              display: inline-flex; /* 关键修改 */
              align-items: center;
              height: -1em; /* 强制与文字同高 */
              margin-top: 0;
            "
          >
            [一键填入]
          </a>
        </p>
      </div>
      <router-link to="/register">没有账号？立即注册</router-link>
    </div>
  </div>
</template>

<!-- 保持原有样式完全不变 -->
<style scoped>
.page-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 20px;
  box-sizing: border-box;
  background: url('../../assets/bg.jpeg') no-repeat center center;
  background-size: cover;
}

.auth-page {
  width: 100%;
  max-width: 400px;
  padding: 4rem;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 20px 20px rgba(0, 0, 0, 0.1);
}

.logo {
  height: 48px;
  width: auto;
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
  width: 93%;
  height: 1rem;
  padding: 0.75rem;
  border: 1px solid #ddd;
  background: #f5f5f5;
  border-radius: 8px;
  font-size: 1rem;
}

button {
  width: 100%;
  padding: 0.65rem;
  margin-top: 0.75rem;
  background-color: #4f46e5;
  color: white;
  border: none;
  border-radius: 8px;
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

.demo-account {
  margin: 1.5rem 0;
  padding: 1rem;
  background-color: #f8fafc;
  border-radius: 4px;
  text-align: center;
  color: #64748b;
  font-size: 0.9rem;
}

.demo-account p {
  margin: 0.5rem 0;
}
</style>
