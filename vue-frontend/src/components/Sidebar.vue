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
  width: 20%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #2c3e50;
  color: white;
}

.sidebar-top {
  flex: 7;
  overflow-y: auto;
}

.sidebar-bottom {
  flex: 3;
  display: flex;
  flex-direction: column;
  padding: 10px;
  border-top: 1px solid #34495e;
}

.new-chat-btn {
  width: 90%;
  margin: 15px auto;
  padding: 10px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
}

.new-chat-btn span {
  font-size: 1.2rem;
  margin-right: 5px;
}

.chat-list {
  overflow-y: auto;
  height: calc(100% - 60px);
}

.sidebar-bottom button {
  margin: 5px 0;
  padding: 10px;
  background-color: transparent;
  color: white;
  border: 1px solid #34495e;
  border-radius: 5px;
  cursor: pointer;
  text-align: left;
  display: flex;
  align-items: center;
}

.sidebar-bottom button:hover {
  background-color: #34495e;
}

.sidebar-bottom button span {
  margin-right: 8px;
}
</style>