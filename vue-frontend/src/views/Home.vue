<script lang="ts">
import { useAuthStore } from '@/stores/auth'
// import { onMounted } from 'vue'

import { defineComponent, ref, computed, onMounted, watch } from 'vue';
import Sidebar from '@/components/Sidebar.vue';
import ChatArea from '@/components/ChatArea.vue';
import type { ChatSession, ChatMessage } from '@/types/chat';
import { HistoryApi } from '@/api/history'
import { AgentApi } from '@/api/agent';
import { useRouter } from 'vue-router';

export default defineComponent({
  name: 'ChatView',
  components: {
    Sidebar,
    ChatArea
  },
  setup() {
    // 模拟数据
    const sessions = ref<ChatSession[]>([]);
    const activeSessionId = ref<string>('');
    const activeSession = ref<ChatSession | null>(null);

// 监听 activeSessionId 变化
  watch(activeSessionId, async (newId) => {
    if (newId) {
      try {
        activeSession.value = await HistoryApi.load(newId);
      } catch (error) {
        console.error('加载会话失败:', error);
        activeSession.value = null;
      }
    } else {
      activeSession.value = null;
    }
  }, { immediate: true }); // 立即执行一次
      // 加载会话列表
      const loadSessions = async () => {
        sessions.value = await HistoryApi.list();
      };

    // 创建新会话
    const createNewSession = async () => {
      console.log("调用了创建新会话")
      const newSession: ChatSession = await HistoryApi.create()
      return newSession;
    };

    // 发送消息
    const sendMessage = async (sessionId: string, content: string) => {
      const session = sessions.value.find(s => s.session_id === sessionId);
      if (!session) return;

      // 用户消息
      const userMessage: ChatMessage = {
        content,
        role: 'user',
        timestamp: new Date()
      };
      session.messages.push(userMessage);

      // 模拟机器人回复
      setTimeout(async() => {
        const botMessage: ChatMessage = {
          content: await AgentApi.askAgent(sessionId, content),
          role: 'system',
          timestamp: new Date()
        };
        session.messages.push(botMessage);
      }, 1000);
    };

    // 处理选择会话
    const handleSelectSession = (sessionId: string) => {
      console.log('Selected session:', sessionId);
      activeSessionId.value = sessionId;
    };

    // 处理新建聊天
    const handleNewChat = async () => {
      await createNewSession();
    };

    // 处理发送消息
    const handleSendMessage = async (content: string) => {
      if (!activeSessionId.value) {
        const newSession = await createNewSession();
        await sendMessage(newSession.session_id, content);
      } else {
        await sendMessage(activeSessionId.value, content);
      }
    };

    // 处理导航
    const router = useRouter()
      
    const handleNavigation = (target: string) => {

      switch(target) {
        case 'agent':
          router.push('/agent/list') // 或 router.push({ name: 'Agent' })
          break
        case 'mcp':
          router.push('/mcp/list') 
          break
        case 'logout':
          router.push('/logout')
          // 通常还会清除登录状态
          break
        default:
          console.warn(`未知导航目标: ${target}`)
      }
    };

    const handleDeleteSession = async (sessionId: string) => {
      try {
        // 调用API删除
        await HistoryApi.delete(sessionId)
        
        // 更新本地数据
        sessions.value = sessions.value.filter(s => s.session_id !== sessionId)
        
        // 如果删除的是当前活动会话
        if (activeSessionId.value === sessionId) {
          activeSessionId.value = ''
        }
      } catch (error) {
        console.error('删除会话失败:', error)
        alert('删除会话失败')
      }
    }

    const authStore = useAuthStore()

    // 初始化认证状态
    onMounted(() => {
      authStore.init().catch(err => console.error('初始化失败:', err));
      loadSessions();
    })

    return {
      sessions,
      activeSessionId,
      activeSession,
      handleSelectSession,
      handleNewChat,
      handleSendMessage,
      handleNavigation,
      handleDeleteSession,
      authStore
    };
  }
});

</script>

<template>
  <div class="chat-container">
    <Sidebar
      :sessions="sessions"
      :activeSessionId="activeSessionId"
      @select-session="handleSelectSession"
      @new-chat="handleNewChat"
      @navigate="handleNavigation"
      @delete-session="handleDeleteSession"
    />
    <ChatArea
      v-if="activeSession"
      :messages="activeSession.messages"
      :sessionTitle="activeSession.title"
      @send-message="handleSendMessage"
    />
    <div v-else class="empty-chat-area">
      <p>请选择或创建一个新的聊天</p>
    </div>
  </div>
</template>

<style scoped>
.chat-container {
  display: flex;
  height: 100vh;
  width: 100%;
}

.empty-chat-area {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f5f5;
  color: #666;
  font-size: 1.2rem;
}
</style>