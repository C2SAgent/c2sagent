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
        <div v-if="message.type === 'text'" class="message-content" v-html="renderMarkdown(message.content)"></div>
        <div v-else-if="message.type === 'doc'" class="message-content">
          <a :href="message.content" target="_blank">{{ t('components.chatArea.viewDocument') }}</a>
        </div>
        <div v-else-if="message.type === 'img'" class="message-content">
          <img :src="message.content" :alt="t('components.chatArea.resultImage')" style="max-width: 100%; max-height: 300px;">
        </div>
        <div v-else-if="message.type === 'thought'" class="message-content">
          <div class="thought-title">{{ t('components.chatArea.thought') }}</div>
          <div class="thought-content" v-html="renderMarkdown(message.content)"></div>
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
        <label class="response-style-toggle">
          <input type="checkbox" v-model="isTimeSeriesProxy" />
          <span class="toggle-container">{{ t('components.chatArea.timeSeries') }}</span>
        </label>

        <label class="response-style-toggle">
          <input type="checkbox" v-model="isAgentProxy" />
          <span class="toggle-container">{{ t('components.chatArea.agentTeam') }}</span>
        </label>

        <label class="response-style-toggle">
          <input type="checkbox" v-model="isThoughtProxy" />
          <span class="toggle-container">{{ t('components.chatArea.deepThought') }}</span>
        </label>

        <label class="file-upload-button">
          <input type="file" @change="handleFileChange" accept=".csv, .txt" style="display: none;" ref="fileInput" />
          {{ t('components.chatArea.uploadFile') }}
          <span v-if="uploadedFile" class="file-name">{{ uploadedFile.name }}</span>
        </label>
      </div>
      <div class="input-container">
        <input
          v-model="newMessage"
          @keyup.enter="sendMessage"
          :placeholder="t('components.chatArea.inputPlaceholder')"
        />
        <button @click="sendMessage">{{ t('common.send') }}</button>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, type PropType, ref, watch, nextTick, onMounted, computed } from 'vue';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import type { ChatMessage } from '@/types/chat';
import { useI18n } from 'vue-i18n';

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
    },
    isAgent: {
      type: Boolean,
      required: true
    },
    isThought: {
      type: Boolean,
      required: true
    },
  },
  emits: ['send-message', 'upload-file', 'update:isTimeSeries', 'update:isAgent', 'update:isThought'],
  setup(props, { emit }) {
    const { t } = useI18n();
    const newMessage = ref('');
    const messagesContainer = ref<HTMLElement | null>(null);
    const uploadedFile = ref<File | null>(null);
    const isTimeSeries = ref(false);
    const isAgent = ref(false);
    const isThought = ref(false);
    const fileInput = ref<HTMLInputElement | null>(null);

    watch(() => props.isTimeSeries, (newVal) => {
      emit('update:isTimeSeries', newVal);
    });

    watch(() => props.isAgent, (newVal) => {
      emit('update:isAgent', newVal);
    });

    watch(() => props.isThought, (newVal) => {
      emit('update:isThought', newVal);
    });

    const isTimeSeriesProxy = computed({
      get: () => props.isTimeSeries,
      set: (val) => emit('update:isTimeSeries', val)
    });

    const isAgentProxy = computed({
      get: () => props.isAgent,
      set: (val) => emit('update:isAgent', val)
    });

    const isThoughtProxy = computed({
      get: () => props.isThought,
      set: (val) => emit('update:isThought', val)
    });

    const renderMarkdown = (content: string) => {
      return DOMPurify.sanitize(marked(content));
    };

    const sendMessage = () => {
      if (newMessage.value.trim() || uploadedFile.value) {
        emit('send-message', newMessage.value.trim());
        newMessage.value = '';
        if (fileInput.value) {
          fileInput.value.value = '';
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
      t,
      newMessage,
      messagesContainer,
      uploadedFile,
      isTimeSeries,
      isAgent,
      isThought,
      renderMarkdown,
      sendMessage,
      handleFileChange,
      formatTime,
      isTimeSeriesProxy,
      isAgentProxy,
      isThoughtProxy,
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

/* 多选框样式 */
.response-style-toggle {
  position: relative;
  display: inline-flex;
  align-items: center;
  cursor: pointer;
  margin-right: 0px;
  user-select: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.response-style-toggle input {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

/* 圆角矩形容器 */
.response-style-toggle .toggle-container {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0px 2px;
  min-width: 80px;
  height: 36px;
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 32px;
  color: #1a202c; /* 未选中字体黑色 */
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

/* 悬停效果 */
.response-style-toggle:hover .toggle-container {
  border-color: #cbd5e0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* 选中状态 - 浅蓝色背景，白色文字 */
.response-style-toggle input:checked + .toggle-container {
  background-color: #63b3ed; /* 浅蓝色 */
  border-color: #63b3ed;
  color: white;
}

/* 聚焦状态 */
.response-style-toggle input:focus + .toggle-container {
  box-shadow: 0 0 0 3px rgba(99, 179, 237, 0.3);
}

/* 激活状态 */
.response-style-toggle.active .toggle-container {
  transform: translateY(1px);
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

.message-content >>> p {
  margin: 0.5em 0;
}

.message-content >>> h1,
.message-content >>> h2,
.message-content >>> h3,
.message-content >>> h4,
.message-content >>> h5,
.message-content >>> h6 {
  margin: 1em 0 0.5em 0;
  font-weight: bold;
}

.message-content >>> h1 {
  font-size: 1.5em;
}

.message-content >>> h2 {
  font-size: 1.3em;
}

.message-content >>> h3 {
  font-size: 1.1em;
}

.message-content >>> ul,
.message-content >>> ol {
  padding-left: 2em;
  margin: 0.5em 0;
}

.message-content >>> li {
  margin: 0.25em 0;
}

.message-content >>> code {
  background-color: #f3f4f6;
  padding: 0.2em 0.4em;
  border-radius: 0.25em;
  font-family: monospace;
}

.message-content >>> pre {
  background-color: #f3f4f6;
  padding: 1em;
  border-radius: 0.5em;
  overflow-x: auto;
  margin: 0.5em 0;
}

.message-content >>> pre code {
  background-color: transparent;
  padding: 0;
}

.message-content >>> blockquote {
  border-left: 3px solid #e2e8f0;
  padding-left: 1em;
  margin: 0.5em 0;
  color: #64748b;
}

.message-content >>> a {
  color: #4299e1;
  text-decoration: none;
}

.message-content >>> a:hover {
  text-decoration: underline;
}

.message-content >>> table {
  border-collapse: collapse;
  width: 100%;
  margin: 0.5em 0;
}

.message-content >>> th,
.message-content >>> td {
  border: 1px solid #e2e8f0;
  padding: 0.5em;
}

.message-content >>> th {
  background-color: #f8fafc;
}

</style>
