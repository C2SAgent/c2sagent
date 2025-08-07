<template>
  <div class="sidebar">
    <div class="sidebar-top">
      <button class="new-chat-btn" @click="emitNewChat">
        <span>+</span> 新建聊天
      </button>
      <div class="chat-list">
        <ChatItem
          v-for="session in sessions"
          :key="session.session_id"
          :session="session"
          :isActive="session.session_id === activeSessionId"
          @click="emitSelectSession(session.session_id)"
          @delete="emitDeleteSession(session.session_id)"
        />
      </div>
    </div>
    <div class="sidebar-bottom">
      <button @click="emitNavigation('agent')">
        <span>👤</span> 管理我的Agent
      </button>
      <button @click="emitNavigation('mcp')">
        <span>⚙️</span> 管理我的Mcp
      </button>
      <button @click="emitNavigation('media')">
        <span>⚙️</span> 管理我的Meida
      </button>
      <button @click="emitNavigation('logout')">
        <span>🚪</span> 退出登录
      </button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, type PropType } from 'vue';
import ChatItem from './ChatItem.vue';
import type { ChatSession } from '@/types/chat';

export default defineComponent({
  name: 'Sidebar',
  components: {
    ChatItem
  },
  props: {
    sessions: {
      type: Array as PropType<ChatSession[]>,
      required: true
    },
    activeSessionId: {
      type: String,
      default: null
    }
  },
  emits: ['select-session', 'new-chat', 'navigate', 'delete-session'],
  setup(props, { emit }) {
    const emitSelectSession = (sessionId: string) => {
      emit('select-session', sessionId);
    };

    const emitNewChat = () => {
      emit('new-chat');
    };

    const emitNavigation = (target: string) => {
      emit('navigate', target);
    };

    const emitDeleteSession = (sessionId: string) => {
      emit('delete-session', sessionId)
    }

    return {
      emitSelectSession,
      emitNewChat,
      emitNavigation,
      emitDeleteSession
    };
  }
});
</script>


<style scoped>
.sidebar {
  width: 260px;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #ffffff;
  color: #1e293b;
  border-right: 1px solid #e2e8f0;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.sidebar-top {
  flex: 7;
  overflow-y: auto;
  padding: 0 0.75rem;
}

.sidebar-bottom {
  flex: 3;
  display: flex;
  flex-direction: column;
  padding: 1rem;
  border-top: 1px solid #e2e8f0;
  gap: 0.5rem;
}

.new-chat-btn {
  width: 100%;
  margin: 1.25rem 0;
  padding: 0.75rem 1rem;
  background: #4299e1;
  color: white;
  border: none;
  border-radius: 0.75rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.95rem;
  font-weight: 500;
  transition: all 0.2s ease;
  box-shadow: 0 2px 6px rgba(66, 153, 225, 0.3);
}

.new-chat-btn:hover {
  background: #3182ce;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(66, 153, 225, 0.4);
}

.new-chat-btn span {
  font-size: 1.3rem;
  margin-right: 0.5rem;
  font-weight: bold;
}

.chat-list {
  overflow-y: auto;
  pointer-events: auto;
  height: calc(100% - 5rem);
  scrollbar-width: thin;
  scrollbar-color: #cbd5e1 #ffffff;
}

.chat-list::-webkit-scrollbar {
  width: 6px;
}

.chat-list::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 3px;
}

.sidebar-bottom button {
  margin: 0.25rem 0;
  padding: 0.75rem 1rem;
  background: #ffffff;
  color: #1e293b;
  border: 1px solid #e2e8f0;
  border-radius: 0.625rem;
  cursor: pointer;
  text-align: left;
  display: flex;
  align-items: center;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.sidebar-bottom button:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
  transform: translateX(3px);
}

.sidebar-bottom button span {
  margin-right: 0.75rem;
  font-size: 1.1rem;
}
</style>
