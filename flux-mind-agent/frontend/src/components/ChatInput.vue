<template>
  <div class="chat-input-container">
    <div class="input-group">
      <input
        v-model="inputMessage"
        type="text"
        :placeholder="inputPlaceholder"
        class="input-field"
        @keyup.enter="sendMessage"
        :disabled="disabled"
      />
      <button 
        @click="sendMessage"
        class="send-button"
        :disabled="disabled || !inputMessage.trim()"
      >
        <span v-if="!disabled">发送</span>
        <span v-else>等待中...</span>
      </button>
    </div>
    <div class="input-tips">
      💡 提示: 输入参数值如 "ht=10" 或提问如 "ht是什么意思"
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  name: 'ChatInput',
  props: {
    disabled: {
      type: Boolean,
      default: false
    }
  },
  emits: ['send'],
  setup(props, { emit }) {
    const inputMessage = ref('')
    
    const inputPlaceholder = computed(() => {
      return props.disabled ? '等待 AI 响应中...' : '请输入消息或参数值 (如: ht=10)...'
    })

    const sendMessage = () => {
      if (inputMessage.value.trim() && !props.disabled) {
        emit('send', inputMessage.value)
        inputMessage.value = ''
      }
    }

    return {
      inputMessage,
      inputPlaceholder,
      sendMessage
    }
  }
}
</script>

<style scoped>
.chat-input-container {
  padding: 20px;
  background: white;
  border-top: 1px solid #ddd;
}

.input-group {
  display: flex;
  gap: 10px;
  margin-bottom: 8px;
}

.input-field {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  font-family: inherit;
  transition: all 0.3s;
  outline: none;
}

.input-field:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.input-field:disabled {
  background: #f5f5f5;
  color: #999;
  cursor: not-allowed;
}

.send-button {
  padding: 12px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s;
}

.send-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.send-button:active:not(:disabled) {
  transform: translateY(0);
}

.send-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.input-tips {
  font-size: 12px;
  color: #999;
  margin-top: 8px;
}
</style>
