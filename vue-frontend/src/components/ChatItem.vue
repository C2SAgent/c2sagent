<template>
  <div
    class="chat-item"
    :class="{ active: isActive }"
    @click="$emit('click')"
  >
    <div class="chat-title">{{ session.title }}</div>
  </div>
  <button class="delete-btn" @click.stop="$emit('delete')">×</button>
</template>

<script lang="ts">
import { defineComponent, type PropType } from 'vue';
import type { ChatSession } from '@/types/chat';

export default defineComponent({
  name: 'ChatItem',
  props: {
    session: {
      type: Object as PropType<ChatSession>,
      required: true
    },
    isActive: {
      type: Boolean,
      default: false
    }
  },
  emits: ['click', 'delete'],
  setup() {
    const formatTime = (date: Date) => {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    return {
      formatTime
    };
  }
});
</script>

<style scoped>
.chat-item {
  padding: 12px 15px;
  border-bottom: 1px solid #34495e;
  cursor: pointer;
}

.chat-item:hover {
  background-color: #34495e;
}

.chat-item.active {
  background-color: #3498db;
}

.chat-title {
  font-weight: bold;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chat-preview {
  font-size: 0.8rem;
  color: #bdc3c7;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-top: 4px;
}

.chat-time {
  font-size: 0.7rem;
  color: #7f8c8d;
  margin-top: 4px;
  text-align: right;
}
</style>