<template>
  <div class="chat-window">
    <div class="messages-container">
      <div 
        v-for="message in messages" 
        :key="message.id"
        :class="['message', `message-${message.type}`]"
      >
        <div class="message-avatar">
          <span v-if="message.type === 'ai'">🤖</span>
          <span v-else-if="message.type === 'user'">👤</span>
          <span v-else>ℹ️</span>
        </div>
        <div class="message-content">
          <div class="message-text">
            {{ message.content }}
            <span v-if="message.streaming" class="streaming-cursor">▋</span>
          </div>
          <div class="message-time">{{ formatTime(message.timestamp) }}</div>
        </div>
      </div>

      <div v-if="loading" class="message message-ai">
        <div class="message-avatar">🤖</div>
        <div class="message-content">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    </div>

    <!-- <div class="status-bar">
      <div class="status-info">
        <span class="status-label">已录入参数:</span>
        <span class="status-value">{{ Object.keys(params).length }}</span>
        <span class="status-separator">|</span>
        <span class="status-label">参数值:</span>
        <span class="status-value">{{ formatParams(params) }}</span>
      </div>
    </div> -->
  </div>
</template>

<script>
export default {
  name: 'ChatWindow',
  props: {
    messages: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    },
    params: {
      type: Object,
      default: () => ({})
    }
  },
  methods: {
    formatTime(timestamp) {
      return new Date(timestamp).toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    },
    formatParams(params) {
      const entries = Object.entries(params)
      if (entries.length === 0) return '无'
      return entries.map(([k, v]) => `${k}=${v}`).join(', ')
    }
  },
  watch: {
    messages: {
      handler() {
        // 自动滚动到底部
        this.$nextTick(() => {
          const container = this.$el.querySelector('.messages-container')
          if (container) {
            container.scrollTop = container.scrollHeight
          }
        })
      },
      deep: true
    }
  }
}
</script>

<style scoped>
.chat-window {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: #f5f5f5;
}

.message {
  display: flex;
  gap: 12px;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-ai {
  justify-content: flex-start;
}

.message-user {
  justify-content: flex-end;
}

.message-system {
  justify-content: center;
}

.message-avatar {
  font-size: 24px;
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.message-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-width: 70%;
}

.message-user .message-content {
  align-items: flex-end;
}

.message-system .message-content {
  align-items: center;
  max-width: 90%;
}

.message-text {
  padding: 12px 16px;
  border-radius: 12px;
  word-break: break-word;
  white-space: pre-wrap;
}

.message-ai .message-text {
  background: #e3f2fd;
  color: #1565c0;
  border-bottom-left-radius: 4px;
}

.message-user .message-text {
  background: #667eea;
  color: white;
  border-bottom-right-radius: 4px;
}

.message-system .message-text {
  background: #fff3cd;
  color: #856404;
  border-radius: 12px;
  font-size: 14px;
}

.message-time {
  font-size: 12px;
  color: #999;
  margin: 0 4px;
}

/* 打字效果 */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #667eea;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    opacity: 0.5;
    transform: translateY(0);
  }
  30% {
    opacity: 1;
    transform: translateY(-10px);
  }
}

.status-bar {
  padding: 12px 20px;
  background: #f0f0f0;
  border-top: 1px solid #ddd;
  font-size: 14px;
}

.status-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.status-label {
  color: #666;
  font-weight: 500;
}

.status-value {
  color: #667eea;
  font-weight: bold;
}

.status-separator {
  color: #ccc;
}

/* 流式输入光标 */
.streaming-cursor {
  display: inline-block;
  margin-left: 2px;
  animation: blink 1s infinite;
  color: #667eea;
  font-weight: bold;
}

@keyframes blink {
  0%, 50% {
    opacity: 1;
  }
  51%, 100% {
    opacity: 0;
  }
}

/* 滚动条样式 */
.messages-container::-webkit-scrollbar {
  width: 8px;
}

.messages-container::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.messages-container::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>
