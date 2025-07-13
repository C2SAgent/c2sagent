<template>
  <div class="chat-area">
    <div class="chat-header">
      <h3>{{ sessionTitle }}</h3>
    </div>
    <div class="messages-container" ref="messagesContainer">
      <div
        v-for="message in messages"
        class="message"
        :class="message.role"
      >
        <div class="message-content">{{ message.content }}</div>
        <div class="message-time">
          {{ formatTime(message.timestamp) }}
        </div>
      </div>
      <!-- 新增：等待响应时的加载指示器 -->
      <div v-if="isWaiting" class="message bot">
        <div class="message-content">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>
    <div class="message-input">
      <input
        v-model="newMessage"
        @keyup.enter="sendMessage"
        placeholder="输入消息..."
      />
      <button @click="sendMessage">发送</button>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, type PropType, ref, watch, nextTick, onMounted } from 'vue';
import type { ChatMessage } from '@/types/chat';

export default defineComponent({
  name: 'ChatArea',
  props: {
    messages: {
      type: Array as PropType<ChatMessage[]>,
      required: true
    },
    sessionTitle: {
      type: String,
      required: true
    },
    isWaiting: { // 新增：接收等待状态
      type: Boolean,
      required: true
    }
  },
  emits: ['send-message'],
  setup(props, { emit }) {
    const newMessage = ref('');
    const messagesContainer = ref<HTMLElement | null>(null);

    const sendMessage = () => {
      if (newMessage.value.trim()) {
        emit('send-message', newMessage.value.trim());
        newMessage.value = '';
      }
    };

    const formatTime = (datetime: Date | string) => {
      const date = typeof datetime === 'string' 
        ? new Date(datetime.replace(' ', 'T')) 
        : datetime;
      
      if (isNaN(date.getTime())) {
        console.warn('Invalid date:', datetime);
        return '--:--';
      }
      
      return date.toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false
      });
    };

    const scrollToBottom = () => {
      nextTick(() => {
        if (messagesContainer.value) {
          messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
        }
      });
    };

    watch(() => props.messages, scrollToBottom, { deep: true });

    onMounted(() => {
      scrollToBottom()
    })

    return {
      newMessage,
      messagesContainer,
      sendMessage,
      formatTime
    };
  }
});
</script>

<style scoped>
.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #ffffff;
  position: relative;
}

.chat-header {
  padding: 1rem 1.5rem;
  background: #ffffff;
  color: #1e293b;
  font-weight: 600;
  font-size: 1.2rem;
  border-bottom: 1px solid #e2e8f0;
  position: sticky;
  top: 0;
  z-index: 10;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  background: #ffffff;
  scroll-behavior: smooth;
}

.messages-container::-webkit-scrollbar {
  width: 6px;
}

.messages-container::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 4px;
}

.message {
  max-width: 80%;
  padding: 1rem 1.25rem;
  border-radius: 1rem;
  position: relative;
  animation: fadeIn 0.3s ease;
  line-height: 1.5;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.message.user {
  margin-left: auto;
  background: #4299e1;
  color: white;
  border-bottom-right-radius: 0.5rem;
  box-shadow: 0 2px 8px rgba(66, 153, 225, 0.2);
}

.message.bot {
  margin-right: auto;
  background: #f8fafc;
  color: #1e293b;
  border: 1px solid #e2e8f0;
  border-bottom-left-radius: 0.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.message-content {
  word-wrap: break-word;
  font-size: 0.95rem;
}

.message-time {
  font-size: 0.75rem;
  color: #64748b;
  text-align: right;
  margin-top: 0.5rem;
}

.message-input {
  display: flex;
  padding: 1rem;
  background: #ffffff;
  border-top: 1px solid #e2e8f0;
  gap: 0.75rem;
  position: sticky;
  bottom: 0;
}

.message-input input {
  flex: 1;
  padding: 0.875rem 1.25rem;
  background: #ffffff;
  color: #1e293b;
  border: 1px solid #cbd5e1;
  border-radius: 1rem;
  outline: none;
  font-size: 0.95rem;
  transition: all 0.2s ease;
}

.message-input input:focus {
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.2);
}

.message-input button {
  padding: 0.875rem 1.5rem;
  background: #4299e1;
  color: white;
  border: none;
  border-radius: 1rem;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

.message-input button:hover {
  background: #3182ce;
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(66, 153, 225, 0.3);
}

.typing-indicator {
  display: flex;
  align-items: center;
  padding: 0.625rem 0;
}

.typing-indicator span {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #94a3b8;
  margin: 0 4px;
  animation: typing 1.4s infinite ease-in-out both;
}

@keyframes typing {
  0%, 80%, 100% {
    transform: translateY(0);
    opacity: 0.5;
  }
  40% {
    transform: translateY(-5px);
    opacity: 1;
  }
}
</style>