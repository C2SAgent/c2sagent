import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/Home.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/Auth/Login.vue'),
      meta: { skipAuthCheck: true }
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/Auth/Register.vue'),
      meta: { skipAuthCheck: true }
    },
    {
      path: '/logout',
      name: 'logout',
      component: () => import('@/views/Auth/Logout.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/agent/create',
      name: 'agent-create',
      component: () => import('@/views/Agent/Create.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/agent/list',
      name: 'agent-list',
      component: () => import('@/views/Agent/List.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/mcp/list',
      name: 'mcp-list',
      component: () => import('@/views/Mcp/List.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/mcp/create',
      name: 'mcp-create',
      component: () => import('@/views/Mcp/Create.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/mcp/:id/tools',
      name: 'mcp-tools',
      component: () => import('@/views/Mcp/Tool.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/media/list',
      name: 'media-list',
      component: () => import('@/views/Media/List.vue'),
      meta: { requiresAuth: true }
    }
  ]
})

router.beforeEach(async (to) => {
  // 跳过登录页的认证检查
  if (to.meta.skipAuthCheck) {
    return true
  }

  const authStore = useAuthStore()

  // 其他页面才需要初始化检查
  if (!authStore.isInitialized) {
    await authStore.init()
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return {
      name: 'login',
      query: { redirect: to.fullPath },
      replace: true
    }
  }

  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    return {
      name: 'home',
      replace: true
    }
  }
})

export default router
