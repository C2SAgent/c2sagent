<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useI18n } from 'vue-i18n';

const { t, locale } = useI18n();

const changeLang = (lang: 'zh-CN' | 'en-US') => {
  locale.value = lang;
};

const router = useRouter();
const authStore = useAuthStore();

const form = ref({
  username: '',
  password: '',
});

const error = ref('');
const isLoading = ref(false);

const fillDemoCredentials = () => {
  form.value.username = 'agent';
  form.value.password = 'agent';
  error.value = '';
};

async function handleSubmit() {
  if (!form.value.username || !form.value.password) {
    error.value = t('errors.required');
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
    error.value = (err as Error).message || t('errors.loginFailed');
  } finally {
    isLoading.value = false;
  }
}
</script>

<template>
  <div class="page-container">
    <!-- 添加语言切换下拉框到右上角 -->
    <div class="language-switcher">
      <select v-model="locale" @change="changeLang(locale as 'zh-CN' | 'en-US')">
        <option value="zh-CN">中文</option>
        <option value="en-US">English</option>
      </select>
    </div>

    <div class="auth-page">
      <h2 style="display: flex; align-items: center; gap: 8px">
        <img src="../../assets/logo.png" alt="logo" class="logo" />
        <span>C2S Agent</span>
      </h2>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="username">{{ t('login.username') }}</label>
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
          <label for="password">{{ t('login.password') }}</label>
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
          {{ isLoading ? t('common.loggingIn') : t('common.login') }}
        </button>
      </form>
      <div class="demo-account">
        <p style="
          margin: 0rem 0;
          display: flex;
          align-items: baseline;
          justify-content: center;
          gap: 8px;
        ">
          <span>{{ t('login.demoAccount') }}</span>
          <a
            @click.prevent="fillDemoCredentials"
            style="
              cursor: pointer;
              color: #4f46e5;
              display: inline-flex;
              align-items: center;
              height: -1em;
              margin-top: 0;
            "
          >
            [{{ t('login.autoFill') }}]
          </a>
        </p>
      </div>
      <router-link to="/register">{{ t('login.noAccount') }}</router-link>
    </div>
  </div>
</template>

<style scoped>
.page-container {
  position: relative; /* 为语言切换器定位做准备 */
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 20px;
  box-sizing: border-box;
  background: url('../../assets/bg.jpeg') no-repeat center center;
  background-size: cover;
}

/* 新增语言切换器样式 */
.language-switcher {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 10;
}

.language-switcher select {
  padding: 8px 32px 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background-color: white;
  /* color: #4f46e5; */
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%234f46e5' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  background-size: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
}

.language-switcher select:hover {
  border-color: #c7d2fe;
  box-shadow: 0 2px 6px rgba(79, 70, 229, 0.2);
}

.language-switcher select:focus {
  outline: none;
  border-color: #4f46e5;
  box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.2);
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
