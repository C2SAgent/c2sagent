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
        <div v-if="message.type === 'text'" class="message-content">{{ message.content }}</div>
        <div v-else-if="message.type === 'doc'" class="message-content">
          <a :href="message.content" target="_blank">查看文档</a>
        </div>
        <div v-else-if="message.type === 'img'" class="message-content">
          <img :src="message.content" alt="分析结果图片" style="max-width: 100%; max-height: 300px;">
        </div>
        <div v-else-if="message.type === 'thought'" class="message-content">
          <div class="thought-title">思考</div>
          <div class="thought-content">{{ message.content }}</div>
        </div>
        <div class="message-time">
          {{ formatTime(message.timestamp) }}
        </div>
      </div>
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
      <div class="input-options">
        <label class="time-series-toggle">
          <input type="checkbox" v-model="isTimeSeriesProxy" />
          时序预测分析
        </label>
        <label class="file-upload-button">
          <input type="file" @change="handleFileChange" accept=".csv, .txt" style="display: none;" ref="fileInput" />
          上传文件
          <span v-if="uploadedFile" class="file-name">{{ uploadedFile.name }}</span>
        </label>
      </div>
      <div class="input-container">
        <input
          v-model="newMessage"
          @keyup.enter="sendMessage"
          placeholder="输入消息..."
        />
        <button @click="sendMessage">发送</button>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, type PropType, ref, watch, nextTick, onMounted, computed } from 'vue';
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
    isWaiting: {
      type: Boolean,
      required: true
    },
    isTimeSeries: {
      type: Boolean,
      required: true
    }
  },
  emits: ['send-message', 'upload-file', 'update:isTimeSeries'],
  setup(props, { emit }) {
    const newMessage = ref('');
    const messagesContainer = ref<HTMLElement | null>(null);
    const uploadedFile = ref<File | null>(null);
    const isTimeSeries = ref(false);
    watch(() => props.isTimeSeries, (newVal) => {
      emit('update:isTimeSeries', newVal);
    });

    const fileInput = ref<HTMLInputElement | null>(null);

    const isTimeSeriesProxy = computed({
      get: () => props.isTimeSeries,
      set: (val) => emit('update:isTimeSeries', val)
    });

    const sendMessage = () => {
      if (newMessage.value.trim() || uploadedFile.value) {
        emit('send-message', newMessage.value.trim());
        newMessage.value = '';
        if (fileInput.value) {
          fileInput.value.value = ''; // 重置文件输入
        }
        uploadedFile.value = null;
      }
    };

    const handleFileChange = (event: Event) => {
      const target = event.target as HTMLInputElement;
      if (target.files && target.files.length > 0) {
        uploadedFile.value = target.files[0];
        emit('upload-file', uploadedFile.value);
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
      uploadedFile,
      isTimeSeries,
      sendMessage,
      handleFileChange,
      formatTime,
      isTimeSeriesProxy,
      fileInput
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

.message-content a {
  color: #4299e1;
  text-decoration: none;
}

.message-content a:hover {
  text-decoration: underline;
}

.message-time {
  font-size: 0.75rem;
  color: #64748b;
  text-align: right;
  margin-top: 0.5rem;
}

.message-input {
  display: flex;
  flex-direction: column;
  padding: 1rem;
  background: #ffffff;
  border-top: 1px solid #e2e8f0;
  gap: 0.75rem;
  position: sticky;
  bottom: 0;
}

.input-options {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.time-series-toggle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #64748b;
  cursor: pointer;
}

.file-upload-button {
  padding: 0.5rem 1rem;
  background: #e2e8f0;
  color: #1e293b;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.file-upload-button:hover {
  background: #cbd5e1;
}

.file-name {
  font-size: 0.75rem;
  color: #475569;
  max-width: 150px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.input-container {
  display: flex;
  gap: 0.75rem;
}

.input-container input {
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

.input-container input:focus {
  border-color: #4299e1;
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.2);
}

.input-container button {
  padding: 0.875rem 1.5rem;
  background: #4299e1;
  color: white;
  border: none;
  border-radius: 1rem;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

.input-container button:hover {
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

.thought-title {
  font-weight: bold;
  margin-bottom: 5px;
  color: #666; /* 深灰色 */
}

.thought-content {
  color: #999; /* 浅灰色 */
}
</style>
