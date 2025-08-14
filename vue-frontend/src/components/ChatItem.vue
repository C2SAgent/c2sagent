<template>
  <div
    class="chat-item"
    :class="{ active: isActive }"
    @click="$emit('click')"
  >
    <div class="chat-title">{{ session.title }}</div>
    <button class="delete-btn" @click.stop="$emit('delete')">×</button>
  </div>
  <!-- <button class="delete-btn" @click.stop="$emit('delete')">×</button> -->
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
  position: relative;
  padding: 0.5rem 1rem;
  border-radius: 0.75rem;
  margin-bottom: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
}

.chat-item:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
}

.chat-item.active {
  background: #76baf2;
  border-color: #76baf2;
  color: white;
  box-shadow: 0 2px 6px rgba(66, 153, 225, 0.3);
}

.chat-title {
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}

/* 修复后的删除按钮样式 */
.delete-btn {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 24px;
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0; /* 默认透明 */
  transition: opacity 0.2s ease, background 0.2s ease; /* 添加过渡效果 */
  z-index: 2;
}

/* 关键修复：确保悬停目标正确 */
.chat-item:hover .delete-btn,
.delete-btn:hover {
  opacity: 1; /* 悬停时显示 */
  background: rgba(239, 68, 68, 0.2);
}
</style>
