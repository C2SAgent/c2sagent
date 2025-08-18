<template>
  <div class="mcp-list-container">
    <div class="header-section">
      <h2 class="page-title">{{ t('views.mcp.list.title') }}</h2>
      <div class="action-buttons">
        <router-link to="/mcp/create" class="primary-btn">
          <span>+</span> {{ t('views.mcp.list.newMcp') }}
        </router-link>
      </div>
    </div>

    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <span>{{ t('views.mcp.list.loading') }}</span>
    </div>

    <div v-else class="mcp-table">
      <table>
        <thead>
          <tr>
            <th class="name-column">{{ t('views.mcp.list.name') }}</th>
            <th class="actions-column">{{ t('views.mcp.list.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="mcp in mcps" :key="mcp.id">
            <td>{{ mcp.name }}</td>
            <td>
              <router-link
                :to="`/mcp/${mcp.id}/tools`"
                class="manage-link"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M20 14.66V20a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h5.34"></path>
                  <polygon points="18 2 22 6 12 16 8 16 8 12 18 2"></polygon>
                </svg>
                {{ t('views.mcp.list.manageTools') }}
              </router-link>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { McpApi } from '@/api/mcp'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const loading = ref(true)
const mcps = ref<any[]>([])

onMounted(async () => {
  try {
    const res = await McpApi.list()
    mcps.value = res.data.data
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.mcp-list-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
}

.action-buttons {
  display: flex;
  gap: 0.75rem;
}

.primary-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background-color: #4299e1;
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
  text-decoration: none;
}

.primary-btn:hover {
  background-color: #3182ce;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  gap: 1rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(66, 153, 225, 0.2);
  border-radius: 50%;
  border-top-color: #4299e1;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.mcp-table {
  width: 100%;
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background-color: #f8fafc;
}

th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #4a5568;
  border-bottom: 1px solid #e2e8f0;
}

td {
  padding: 1rem;
  border-bottom: 1px solid #e2e8f0;
  color: #4a5568;
}

.name-column {
  width: 70%;
}

.actions-column {
  width: 30%;
}

.manage-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #4299e1;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s;
}

.manage-link:hover {
  color: #3182ce;
  text-decoration: underline;
}

.manage-link svg {
  flex-shrink: 0;
}
</style>
