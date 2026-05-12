<template>
  <div v-if="true" class="modal-overlay" @click.self="$emit('cancel')">
    <div class="modal-content">
      <div class="modal-header">
        <h2>{{ title }}</h2>
        <button class="close-btn" @click="$emit('cancel')">×</button>
      </div>
      
      <div class="modal-body">
        <p class="modal-prompt">请输入信息继续对话：</p>
        <input
          v-model="inputValue"
          type="text"
          placeholder="输入内容..."
          class="modal-input"
          @keyup.enter="confirmInput"
          ref="inputRef"
        />
      </div>

      <div class="modal-footer">
        <button @click="$emit('cancel')" class="btn btn-cancel">取消</button>
        <button @click="confirmInput" class="btn btn-confirm">确认</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, nextTick } from 'vue'

export default {
  name: 'InputModal',
  props: {
    title: {
      type: String,
      default: '用户输入'
    }
  },
  emits: ['confirm', 'cancel'],
  setup(props, { emit }) {
    const inputValue = ref('')
    const inputRef = ref(null)

    const confirmInput = () => {
      if (inputValue.value.trim()) {
        emit('confirm', inputValue.value)
        inputValue.value = ''
      }
    }

    nextTick(() => {
      inputRef.value?.focus()
    })

    return {
      inputValue,
      inputRef,
      confirmInput
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.modal-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  max-width: 500px;
  width: 90%;
  animation: slideUp 0.3s;
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  transition: color 0.3s;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 20px;
}

.modal-prompt {
  margin: 0 0 12px 0;
  color: #666;
  font-size: 14px;
}

.modal-input {
  width: 100%;
  padding: 10px 12px;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.3s;
}

.modal-input:focus {
  border-color: #667eea;
}

.modal-footer {
  padding: 20px;
  border-top: 1px solid #eee;
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s;
}

.btn-cancel {
  background: #f0f0f0;
  color: #333;
}

.btn-cancel:hover {
  background: #e0e0e0;
}

.btn-confirm {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-confirm:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}
</style>
