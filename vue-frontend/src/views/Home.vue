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
      :isTimeSeries="isTimeSeries"
      :isAgent="isAgent"
      @send-message="handleSendMessage"
      @upload-file="handleFileUpload"
      @update:isTimeSeries="val => isTimeSeries = val"
      @update:isAgent="val => isAgent = val"
    />
    <div v-else class="empty-chat-area">
      <p>请选择或创建一个新的任务</p>
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
    const isWaiting = ref(false);
    const uploadedFile = ref<File | undefined>(undefined);
    const isTimeSeries = ref(false);
    const isAgent = ref(false);

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
      const newSession: ChatSession = await HistoryApi.create()
      return newSession;
    };

    const handleFileUpload = (file: File) => {
      uploadedFile.value = file;
    };

const sendMessage = async (sessionId: string, content: string) => {
  const session = sessions.value.find(s => s.session_id === sessionId);
  if (!session) return;

  // 用户消息
  const userMessage: ChatMessage = {
    content,
    role: 'user',
    type: 'text',
    timestamp: new Date()
  };
  session.messages.push(userMessage);

  isWaiting.value = true;

  // 定义更新内容的辅助函数
  const updateContent = (msg: ChatMessage, newData: string) => {
    const index = session.messages.indexOf(msg);
    if (index !== -1) {
      const newMsg = {...msg, content: msg.content + newData};
      session.messages.splice(index, 1, newMsg);
      return newMsg; // 返回更新后的消息
    }
    return msg;
  };

  try {
    // 获取流式响应
    const stream = await AgentApi.askAgentStreaming(
      sessionId,
      content,
      isTimeSeries.value,
      isAgent.value,
      uploadedFile.value
    );

    const reader = stream.getReader();
    let currentMessage: ChatMessage | null = null;
    let currentType: string | null = null;
    let done = false;

    while (!done) {
      const { value, done: streamDone } = await reader.read();
      done = streamDone;

      if (value) {
        const textDecoder = new TextDecoder();
        const chunk = textDecoder.decode(value);
        const lines = chunk.split('\n\n').filter(line => line.trim());

        for (const line of lines) {
          try {
            const parsed = JSON.parse(line);
            const { event, data } = parsed;

            if (event === 'end') {
              currentMessage = null;
              currentType = null;
              continue;
            }

            // 特殊类型处理：img和doc总是创建新消息
            if (event === 'img' || event === 'doc') {
              currentMessage = {
                content: data,
                role: 'system',
                type: event,
                timestamp: new Date()
              };
              session.messages.push(currentMessage);
              continue;
            }

            if (event !== currentType || !currentMessage) {
              // 类型变化或没有当前消息，创建新消息
              currentType = event;
              currentMessage = {
                content: data,
                role: 'system',
                type: event === 'thought' ? 'thought' : 'text',
                timestamp: new Date()
              };
              session.messages.push(currentMessage);
            } else {
              // 类型相同且存在当前消息，使用updateContent更新内容
              currentMessage = updateContent(currentMessage, data);
            }
          } catch (e) {
            console.error('解析流数据失败:', e);
          }
        }
      }
    }
  } catch (error) {
    console.error('请求失败:', error);
    session.messages.push({
      content: '请求失败，请重试',
      role: 'system',
      type: 'text',
      timestamp: new Date()
    });
  } finally {
    isWaiting.value = false;
    uploadedFile.value = undefined;
  }
};

    const handleSelectSession = (sessionId: string) => {
      activeSessionId.value = sessionId;
    };

    const handleNewChat = async () => {
      const newSession = await createNewSession();
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
        case 'media':
          router.push('/media/list')
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
      isWaiting,
      isTimeSeries,
      isAgent,
      handleSelectSession,
      handleNewChat,
      handleSendMessage,
      handleNavigation,
      handleDeleteSession,
      handleFileUpload,
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
