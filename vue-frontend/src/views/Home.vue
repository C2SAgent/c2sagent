<template>
  <div class="chat-container">
    <Sidebar
      :sessions="displayedSessions"
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
      :isThought="isThought"
      @send-message="handleSendMessage"
      @upload-file="handleFileUpload"
      @update:isTimeSeries="val => isTimeSeries = val"
      @update:isAgent="val => isAgent = val"
      @update:isThought="val => isThought = val"
      @stop-message="handleStopMessage"
    />
    <div v-else class="empty-chat-area">
      <p>{{ t('views.home.selectOrCreate') }}</p>
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
import { useI18n } from 'vue-i18n';

export default defineComponent({
  name: 'ChatView',
  components: {
    Sidebar,
    ChatArea
  },
  setup() {
    const { t } = useI18n();
    const sessions = ref<ChatSession[]>([]);
    const activeSessionId = ref<string>('');
    const activeSession = ref<ChatSession | null>(null);
    const isWaiting = ref(false);
    const uploadedFile = ref<File | undefined>(undefined);
    const isTimeSeries = ref(false);
    const isAgent = ref(false);
    const isThought = ref(false);
    const shouldStop = ref(false);

    const displayedSessions = computed(() => sessions.value);

    watch(activeSessionId, async (newId) => {
      if (newId) {
        try {
          const freshData = await HistoryApi.load(newId);
          sessions.value = sessions.value.map(s =>
            s.session_id === newId ? freshData : s
          );
          activeSession.value = freshData;
        } catch (error) {
          console.error(t('errors.loadFailed'), error);
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

    const handleStopMessage = () => {
      shouldStop.value = true;
    };

const sendMessage = async (sessionId: string, content: string) => {
  const session = sessions.value.find(s => s.session_id === sessionId);
  if (!session) return;

  const userMessage: ChatMessage = {
    content,
    role: 'user',
    type: 'text',
    timestamp: new Date()
  };
  session.messages.push(userMessage);

  isWaiting.value = true;
  shouldStop.value = false;

  // 添加一个变量来存储更新标题的计时器
  let updateTitleTimer: number | null = null;

  const updateContent = (msg: ChatMessage, newData: string) => {
    const index = session.messages.indexOf(msg);
    if (index !== -1) {
      const newMsg = {...msg, content: msg.content + newData};
      session.messages.splice(index, 1, newMsg);
      return newMsg;
    }
    return msg;
  };

  try {
    const stream = await AgentApi.askAgentStreaming(
      sessionId,
      content,
      isTimeSeries.value,
      isAgent.value,
      isThought.value,
      uploadedFile.value
    );

    const reader = stream.getReader();
    let currentMessage: ChatMessage | null = null;
    let currentType: string | null = null;
    let done = false;

    while (!done && !shouldStop.value) {
      try {
        const { value, done: streamDone } = await reader.read();
        done = streamDone;

        if (shouldStop.value) {
          await reader.cancel();
          break;
        }

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
                currentType = event;
                currentMessage = {
                  content: data,
                  role: 'system',
                  type: event === 'thought' ? 'thought' : 'text',
                  timestamp: new Date()
                };
                session.messages.push(currentMessage);
              } else {
                currentMessage = updateContent(currentMessage, data);
              }
            } catch (e) {
              console.error(t('errors.parseFailed'), e);
            }
          }
        }
      } catch (error) {
        done = true;
      }
    }
  } catch (error) {
    console.error(t('errors.requestFailed'), error);
    session.messages.push({
      content: t('errors.requestFailed'),
      role: 'system',
      type: 'text',
      timestamp: new Date()
    });
  } finally {
    isWaiting.value = false;
    uploadedFile.value = undefined;
    shouldStop.value = false;

    // 清除之前的计时器（如果有）
    if (updateTitleTimer) {
      clearTimeout(updateTitleTimer);
    }

    // 设置新的计时器，6秒后更新标题
    updateTitleTimer = setTimeout(async () => {
      try {
        const freshData = await HistoryApi.load(sessionId);
        const updatedSession = sessions.value.find(s => s.session_id === sessionId);
        if (updatedSession && freshData.title !== updatedSession.title) {
          updatedSession.title = freshData.title;
          // 这里只需要更新title，不会触发整个组件的刷新
        }
      } catch (error) {
        console.error(t('errors.updateTitleFailed'), error);
      }
    }, 5000) as unknown as number;
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
        case 'logout':
          router.push('/logout')
          break
        default:
          console.warn(t('errors.unknownNavTarget', { target }))
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
        console.error(t('errors.deleteSessionFailed'), error)
        alert(t('errors.deleteSessionFailed'))
      }
    }

    const authStore = useAuthStore()

    onMounted(() => {
      authStore.init().catch(err => console.error(t('errors.initFailed'), err));
      loadSessions();
    })

    return {
      sessions,
      activeSessionId,
      activeSession,
      isWaiting,
      isTimeSeries,
      isAgent,
      isThought,
      handleSelectSession,
      handleNewChat,
      handleSendMessage,
      handleNavigation,
      handleDeleteSession,
      handleFileUpload,
      handleStopMessage,
      displayedSessions,
      authStore,
      t
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
