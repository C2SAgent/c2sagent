<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import { onMounted } from 'vue'

const authStore = useAuthStore()

// 初始化认证状态
onMounted(() => {
  authStore.init().catch(err => console.error('初始化失败:', err))
})
</script>

<template>
  <div class="main-layout">
    <!-- 侧边栏导航 -->
    <aside class="sidebar" v-if="authStore.isAuthenticated">
      <div class="user-info">
        <h3>欢迎, {{ authStore.user?.name }}</h3>
      </div>
      
      <nav class="menu">
        <router-link to="/home" class="menu-item">首页</router-link>
        
        <div class="menu-group">
          <div class="menu-title">智能体管理</div>
          <router-link to="/agent/create" class="submenu-item">创建智能体</router-link>
          <router-link to="/agent/list" class="submenu-item">智能体列表</router-link>
        </div>
        <div class="menu-group">
          <div class="menu-title">MCP管理</div>
          <router-link to="/mcp/create" class="submenu-item">创建MCP</router-link>
          <router-link to="/mcp/list" class="submenu-item">MCP列表</router-link>
        </div>

        <router-link to="/logout" class="menu-item">退出登录</router-link>
      </nav>
    </aside>
    
    <!-- 主内容区 -->
    <main class="content">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.main-layout {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 250px;
  background: #f5f5f5;
  padding: 20px;
  border-right: 1px solid #e0e0e0;
}

.user-info {
  padding: 10px 0;
  margin-bottom: 20px;
  border-bottom: 1px solid #ddd;
}

.menu {
  display: flex;
  flex-direction: column;
}

.menu-item, .submenu-item {
  padding: 10px 15px;
  margin: 5px 0;
  text-decoration: none;
  color: #333;
  border-radius: 4px;
}

.menu-item:hover, .submenu-item:hover {
  background: #e9e9e9;
}

.menu-group {
  margin: 15px 0;
}

.menu-title {
  font-weight: bold;
  padding: 10px 15px;
  color: #666;
}

.submenu-item {
  padding-left: 30px;
  font-size: 0.9em;
}

.content {
  flex: 1;
  padding: 20px;
}
</style>