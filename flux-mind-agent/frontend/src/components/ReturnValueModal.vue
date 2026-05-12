<template>
  <div v-if="true" class="modal-overlay" @click.self="$emit('cancel')">
    <div class="modal-content">
      <div class="modal-header">
        <h2>工具返回值输入</h2>
        <button class="close-btn" @click="$emit('cancel')">×</button>
      </div>
      
      <div class="modal-body" v-if="toolInfo">
        <div class="tool-info">
          <div class="info-item">
            <span class="label">工具名称:</span>
            <span class="value">{{ toolInfo.tool }}</span>
          </div>
          <div class="info-item">
            <span class="label">参数:</span>
            <span class="value">{{ JSON.stringify(toolInfo.parameter) }}</span>
          </div>
          <div class="info-item">
            <span class="label">目的:</span>
            <span class="value">{{ toolInfo.purpose }}</span>
          </div>
        </div>

        <div class="input-section">
          <p class="section-title">请输入该工具调用的返回值：</p>
          <textarea
            v-model="returnValue"
            placeholder="输入 JSON 格式或文本..."
            class="return-input"
            rows="6"
          ></textarea>
        </div>
      </div>

      <div class="modal-footer">
        <button @click="$emit('cancel')" class="btn btn-cancel">取消</button>
        <button @click="confirmReturnValue" class="btn btn-confirm">提交</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'

export default {
  name: 'ReturnValueModal',
  props: {
    toolInfo: {
      type: Object,
      required: true
    }
  },
  emits: ['confirm', 'cancel'],
  setup(props, { emit }) {
    const returnValue = ref('')

    const confirmReturnValue = () => {
      if (returnValue.value.trim()) {
        emit('confirm', returnValue.value)
        returnValue.value = ''
      }
    }

    watch(() => props.toolInfo, () => {
      returnValue.value = ''
    })

    return {
      returnValue,
      confirmReturnValue
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
  z-index: 1001;
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
  max-width: 600px;
  width: 90%;
  animation: slideUp 0.3s;
  max-height: 80vh;
  overflow-y: auto;
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.modal-header h2 {
  margin: 0;
  font-size: 18px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: white;
  cursor: pointer;
  opacity: 0.8;
  transition: opacity 0.3s;
}

.close-btn:hover {
  opacity: 1;
}

.modal-body {
  padding: 20px;
}

.tool-info {
  background: #f5f5f5;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
}

.info-item {
  display: flex;
  gap: 12px;
  margin-bottom: 10px;
  font-size: 14px;
}

.info-item:last-child {
  margin-bottom: 0;
}

.label {
  color: #667eea;
  font-weight: 600;
  min-width: 80px;
}

.value {
  color: #333;
  word-break: break-all;
}

.input-section {
  margin-bottom: 20px;
}

.section-title {
  margin: 0 0 12px 0;
  color: #333;
  font-weight: 600;
  font-size: 14px;
}

.return-input {
  width: 100%;
  padding: 12px;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 13px;
  font-family: 'Courier New', monospace;
  outline: none;
  resize: vertical;
  transition: border-color 0.3s;
}

.return-input:focus {
  border-color: #667eea;
}

.modal-footer {
  padding: 20px;
  border-top: 1px solid #eee;
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  background: #f9f9f9;
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
