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
import { defineComponent, type PropType, ref, watch, nextTick } from 'vue';
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

    const formatTime = (input: Date | string | number | null) => {
      // 处理 null/undefined
      if (!input) return '--:--';
      
      // 统一转换为 Date 对象
      const date = input instanceof Date ? input : new Date(input);
      
      // 验证日期有效性
      if (isNaN(date.getTime())) {
        console.warn('Invalid date:', input);
        return '--:--';
      }
      
      return date.toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false // 使用24小时制（可选）
      });
    };

    // 自动滚动到底部
    const scrollToBottom = () => {
      nextTick(() => {
        if (messagesContainer.value) {
          messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
        }
      });
    };

    watch(() => props.messages, scrollToBottom, { deep: true });

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
  background-color: #f5f5f5;
}

.chat-header {
  padding: 15px;
  background-color: #3498db;
  color: white;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.messages-container {
  flex: 1;
  padding: 15px;
  overflow-y: auto;
}

.message {
  margin-bottom: 15px;
  max-width: 70%;
  padding: 10px 15px;
  border-radius: 18px;
  position: relative;
}

.message.user {
  margin-left: auto;
  background-color: #3498db;
  color: white;
  border-bottom-right-radius: 5px;
}

.message.system {
  margin-right: auto;
  background-color: white;
  color: #333;
  border-bottom-left-radius: 5px;
  box-shadow: 0 1px 1px rgba(0, 0, 0, 0.1);
}

.message-content {
  word-wrap: break-word;
}

.message-time {
  font-size: 0.7rem;
  color: #7f8c8d;
  text-align: right;
  margin-top: 5px;
}

.message-input {
  display: flex;
  padding: 15px;
  background-color: white;
  border-top: 1px solid #ddd;
}

.message-input input {
  flex: 1;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 20px;
  outline: none;
}

.message-input button {
  margin-left: 10px;
  padding: 10px 20px;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
}

.message-input button:hover {
  background-color: #2980b9;
}
</style>