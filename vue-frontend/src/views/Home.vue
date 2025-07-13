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
      :isWaiting="isWaiting"
      @send-message="handleSendMessage"
    />
    <div v-else class="empty-chat-area">
      <p>请选择或创建一个新的聊天</p>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, watch } from 'vue';
import Sidebar from '@/components/Sidebar.vue';
import ChatArea from '@/components/ChatArea.vue';
import type { ChatSession, ChatMessage } from '@/types/chat';
import { HistoryApi } from '@/api/history';
import { AgentApi } from '@/api/agent';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';

export default defineComponent({
  name: 'ChatView',
  components: {
    Sidebar,
    ChatArea
  },
  setup() {
    const sessions = ref<ChatSession[]>([]);
    const activeSessionId = ref<string>('');
    const activeSession = ref<ChatSession | null>(null);
    const isWaiting = ref(false); // 新增：等待响应状态

    watch(activeSessionId, async (newId) => {
      if (newId) {
        try {
          const freshData = await HistoryApi.load(newId);
          sessions.value = sessions.value.map(s => 
            s.session_id === newId ? freshData : s
          );
          activeSession.value = freshData;
        } catch (error) {
          console.error('加载失败:', error);
          activeSession.value = null;
        }
      } else {
        activeSession.value = null;
      }
    }, { immediate: true });

    const loadSessions = async () => {
      sessions.value = await HistoryApi.list();
    };

    const createNewSession = async () => {
      console.log("调用了创建新会话")
      const newSession: ChatSession = await HistoryApi.create()
      return newSession;
    };

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
      
      // 设置等待状态为true
      isWaiting.value = true;
      
      try {
        // 请求AI响应
        const botResponse = await AgentApi.askAgent(sessionId, content);
        
        // 添加AI消息
        const botMessage: ChatMessage = {
          content: botResponse,
          role: 'bot',
          timestamp: new Date()
        };
        session.messages.push(botMessage);
      } catch (error) {
        console.error('请求失败:', error);
        // 添加错误消息
        const errorMessage: ChatMessage = {
          content: '请求失败，请重试',
          role: 'bot',
          timestamp: new Date()
        };
        session.messages.push(errorMessage);
      } finally {
        // 无论成功失败都取消等待状态
        isWaiting.value = false;
      }
    };

    const handleSelectSession = (sessionId: string) => {
      activeSessionId.value = sessionId;
    };

    const handleNewChat = async () => {
      const newSession = await createNewSession();
      
      // 修复点：添加新会话到列表并激活
      sessions.value = [newSession, ...sessions.value];
      activeSessionId.value = newSession.session_id;
    };

    const handleSendMessage = async (content: string) => {
      if (!activeSessionId.value) {
        const newSession = await createNewSession();
        activeSessionId.value = newSession.session_id;
        await sendMessage(newSession.session_id, content);
      } else {
        await sendMessage(activeSessionId.value, content);
      }
    };

    const router = useRouter()
    const handleNavigation = (target: string) => {
      switch(target) {
        case 'agent':
          router.push('/agent/list')
          break
        case 'mcp':
          router.push('/mcp/list') 
          break
        case 'logout':
          router.push('/logout')
          break
        default:
          console.warn(`未知导航目标: ${target}`)
      }
    };

    const handleDeleteSession = async (sessionId: string) => {
      try {
        await HistoryApi.delete(sessionId)
        sessions.value = sessions.value.filter(s => s.session_id !== sessionId)
        if (activeSessionId.value === sessionId) {
          activeSessionId.value = ''
        }
      } catch (error) {
        console.error('删除会话失败:', error)
        alert('删除会话失败')
      }
    }

    const authStore = useAuthStore()

    onMounted(() => {
      authStore.init().catch(err => console.error('初始化失败:', err));
      loadSessions();
    })

    return {
      sessions,
      activeSessionId,
      activeSession,
      isWaiting, // 暴露等待状态
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
<style scoped>
.chat-container {
  display: flex;
  height: 100vh;
  width: 100%;
  background-color: #f8fafc;
  color: #1e293b;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.empty-chat-area {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #ffffff;
  color: #64748b;
  font-size: 1.2rem;
  padding: 2rem;
  text-align: center;
  border-left: 1px solid #e2e8f0;
}
</style>