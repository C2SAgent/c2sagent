<script setup lang="ts">
import { ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import { useI18n } from 'vue-i18n';
import type { UserCreate } from '@/types/auth';

const { t } = useI18n();
const router = useRouter();
const authStore = useAuthStore();

const llmOptions = ref([
  { name: 'deepseek', url: 'https://api.deepseek.com/v1' },
  { name: 'doubao-seed-1-6', url: 'https://ark.cn-beijing.volces.com/api/v3' }
]);

const form = ref<UserCreate>({
  name: '',
  password: '',
  core_llm_name: '',
  core_llm_url: '',
  core_llm_key: '',
});

const error = ref('');
const isLoading = ref(false);

// 监听LLM选择变化，自动填充URL
watch(() => form.value.core_llm_name, (newValue) => {
  if (newValue) {
    const selectedLLM = llmOptions.value.find(option => option.name === newValue);
    if (selectedLLM) {
      form.value.core_llm_url = selectedLLM.url;
    }
  }
});

async function handleSubmit() {
  // 验证是否选择了LLM
  if (!form.value.core_llm_name || !llmOptions.value.some(option => option.name === form.value.core_llm_name)) {
    error.value = t('errors.selectLLM');
    return;
  }

  // 验证其他必填字段
  if (!form.value.name || !form.value.password) {
    error.value = t('errors.required');
    return;
  }

  try {
    isLoading.value = true;
    error.value = '';
    await authStore.register(form.value);
    router.push('/');
  } catch (err) {
    error.value = t('errors.registerFailed');
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
          <label for="username">{{ t('register.username') }}</label>
          <input
            id="username"
            v-model="form.name"
            type="text"
            required
            autocomplete="username"
            @input="error = ''"
          />
        </div>
        <div class="form-group">
          <label for="password">{{ t('register.password') }}</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            required
            autocomplete="new-password"
            @input="error = ''"
          />
        </div>
        <div class="form-group">
          <label for="core_llm_name">{{ t('register.coreLLMName') }}</label>
          <select
            id="core_llm_name"
            v-model="form.core_llm_name"
            required
            @change="error = ''"
          >
            <option value="" disabled selected>{{ t('register.selectLLM') }}</option>
            <option v-for="option in llmOptions" :key="option.name" :value="option.name">
              {{ option.name }}
            </option>
          </select>
        </div>
        <div class="form-group">
          <label for="core_llm_url">{{ t('register.coreLLMUrl') }}</label>
          <input
            id="core_llm_url"
            v-model="form.core_llm_url"
            type="text"
            readonly
            @input="error = ''"
          />
        </div>
        <div class="form-group">
          <label for="core_llm_key">{{ t('register.coreLLMKey') }}</label>
          <input
            id="core_llm_key"
            v-model="form.core_llm_key"
            type="text"
            @input="error = ''"
          />
        </div>
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
        <button type="submit" :disabled="isLoading">
          {{ isLoading ? t('common.registering') : t('common.register') }}
        </button>
      </form>
      <router-link to="/login">{{ t('register.haveAccount') }}</router-link>
    </div>
  </div>
</template>

<style scoped>
/* 保持原有的样式不变，只添加select样式 */
select {
  width: 100%;
  height: 2.5rem;
  padding: 0.75rem;
  border: 1px solid #ddd;
  background: #f5f5f5;
  border-radius: 8px;
  font-size: 1rem;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%234f46e5' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 10px center;
  background-size: 16px;
}

select:focus {
  outline: none;
  border-color: #4f46e5;
  box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.2);
}

/* 其他原有样式保持不变 */
.page-container {
  position: relative;
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
</style>
