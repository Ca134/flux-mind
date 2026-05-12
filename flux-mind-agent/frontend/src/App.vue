<template>
  <div class="app-container">
    <div class="chat-wrapper">
      <ChatWindow 
        :messages="messages" 
        :loading="isLoading"
        :params="recordedParams"
      />
      <ChatInput 
        @send="handleSendMessage"
        :disabled="!inputEnabled && !sessionStatus.includes('waiting')"
      />
    </div>

    <!-- 弹窗：请求 return_value -->
    <ReturnValueModal
      v-if="showReturnValueModal"
      :tool-info="currentToolInfo"
      @confirm="handleReturnValue"
      @cancel="showReturnValueModal = false"
    />

    <!-- 弹窗：设计结果表格 -->
    <DesignResultTable
      v-if="showDesignResult"
      :result="designResult"
      @close="showDesignResult = false"
    />
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import ChatWindow from './components/ChatWindow.vue'
import ChatInput from './components/ChatInput.vue'
import ReturnValueModal from './components/ReturnValueModal.vue'
import DesignResultTable from './components/DesignResultTable.vue'
import {
  initializeSocket,
  sendUserInput,
  sendReturnValue,
  clearMessageCallback,
  getSocketState,
  startSession as requestSessionStart
} from './services/messagePoller'
import { apiService } from './services/api'

const MESSAGE_STORAGE_KEY = 'inductor-design-chat-messages'

export default {
  name: 'App',
  components: {
    ChatWindow,
    ChatInput,
    ReturnValueModal,
    DesignResultTable
  },
  setup() {
    const loadStoredMessages = () => {
      try {
        const stored = sessionStorage.getItem(MESSAGE_STORAGE_KEY)
        return stored
          ? JSON.parse(stored).map(message => ({
              ...message,
              streaming: false
            }))
          : []
      } catch (error) {
        console.error('Failed to load stored messages:', error)
        return []
      }
    }

    const messages = ref(loadStoredMessages())
    const isLoading = ref(false)
    const inputEnabled = ref(false)  // 控制输入框是否启用
    const showReturnValueModal = ref(false)
    const sessionStatus = ref('idle')
    const recordedParams = ref({})
    const missingParams = ref([])

    const currentToolInfo = ref(null)
    const streamingMessages = ref({})  // 存储流式消息 {message_id: message_index}
    const showDesignResult = ref(false)  // 控制设计结果弹窗
    const designResult = ref({})  // 存储设计结果数据
    const streamQueues = new Map()
    let persistTimer = null

    const persistMessages = () => {
      sessionStorage.setItem(MESSAGE_STORAGE_KEY, JSON.stringify(messages.value))
    }

    const schedulePersistMessages = () => {
      if (persistTimer) {
        return
      }

      persistTimer = setTimeout(() => {
        persistTimer = null
        persistMessages()
      }, 80)
    }

    const clearStreamQueue = (messageId) => {
      const queueState = streamQueues.get(messageId)
      if (queueState?.timer) {
        clearTimeout(queueState.timer)
      }
      streamQueues.delete(messageId)
      delete streamingMessages.value[messageId]
    }

    const finalizeStreamingMessage = (messageId) => {
      const messageIndex = streamingMessages.value[messageId]
      if (messageIndex !== undefined && messages.value[messageIndex]) {
        messages.value[messageIndex].streaming = false
      }

      clearStreamQueue(messageId)
      schedulePersistMessages()
    }

    const pumpStreamingMessage = (messageId) => {
      const queueState = streamQueues.get(messageId)
      if (!queueState || queueState.timer) {
        return
      }

      const step = () => {
        const currentState = streamQueues.get(messageId)
        const messageIndex = streamingMessages.value[messageId]

        if (!currentState || messageIndex === undefined || !messages.value[messageIndex]) {
          clearStreamQueue(messageId)
          return
        }

        if (currentState.buffer.length > 0) {
          const charsPerTick = currentState.buffer.length > 24 ? 3 : 2
          messages.value[messageIndex].content += currentState.buffer.slice(0, charsPerTick)
          currentState.buffer = currentState.buffer.slice(charsPerTick)
          schedulePersistMessages()
          currentState.timer = setTimeout(step, 18)
          return
        }

        currentState.timer = null
        if (currentState.isComplete) {
          finalizeStreamingMessage(messageId)
        }
      }

      queueState.timer = setTimeout(step, 0)
    }

    const handleStreamingChunk = ({ message_id: messageId, content = '', is_complete: isComplete = false }) => {
      let messageIndex = streamingMessages.value[messageId]

      if (messageIndex === undefined) {
        isLoading.value = false
        messages.value.push({
          id: `stream-${messageId}`,
          type: 'ai',
          content: '',
          timestamp: new Date(),
          streaming: true
        })
        messageIndex = messages.value.length - 1
        streamingMessages.value[messageId] = messageIndex
      }

      const queueState = streamQueues.get(messageId) || {
        buffer: '',
        isComplete: false,
        timer: null
      }

      queueState.buffer += content
      queueState.isComplete = queueState.isComplete || isComplete
      streamQueues.set(messageId, queueState)

      if (!queueState.buffer && queueState.isComplete && !queueState.timer) {
        finalizeStreamingMessage(messageId)
        return
      }

      pumpStreamingMessage(messageId)
      schedulePersistMessages()
    }

    const resetStreamingState = () => {
      Array.from(streamQueues.keys()).forEach(clearStreamQueue)
      streamingMessages.value = {}
    }

    // 添加系统消息
    const addMessage = (type, content) => {
      messages.value.push({
        id: Date.now(),
        type, // 'ai', 'user', 'system'
        content,
        timestamp: new Date()
      })
      persistMessages()
    }

    // 处理来自后端的消息
    const handleBackendMessage = (message) => {
      const { type, content } = message

      switch (type) {
        case 'ai_message':
          addMessage('ai', content)
          break
        case 'ai_message_stream':
          handleStreamingChunk(message)
          break
        case 'request_user_input':
          // 启用输入框，用户可以直接输入
          inputEnabled.value = true
          isLoading.value = false  // 停止加载状态
          addMessage('system', content)
          break
        case 'request_return_value':
          // 需要 return_value 时才显示弹窗
          currentToolInfo.value = content
          showReturnValueModal.value = true
          addMessage('system', `工具 "${content.tool}" 需要返回值`)
          break
        case 'error':
          addMessage('system', `❌ 错误: ${content}`)
          inputEnabled.value = false
          break
        case 'session_end':
          addMessage('system', `✅ ${content}`)
          sessionStatus.value = 'ended'
          isLoading.value = false
          inputEnabled.value = false
          break
        case 'design_result':
          designResult.value = content
          addMessage('system', '优化设计已完成。结果已保存到当前会话上下文中，你可以继续询问推荐理由、方案对比或关键参数解释。')
          inputEnabled.value = true
          break
      }
    }

    // 处理用户发送消息
    const handleSendMessage = (userMessage) => {
      addMessage('user', userMessage)
      sendUserInput(userMessage)
      inputEnabled.value = false  // 发送后禁用输入框
      isLoading.value = true  // 显示加载状态
    }

    // 处理 return_value（ReturnValueModal）
    const handleReturnValue = (returnValue) => {
      showReturnValueModal.value = false
      addMessage('user', `[return_value]: ${returnValue}`)
      sendReturnValue(returnValue)
      isLoading.value = true  // 显示加载状态
    }

    // 更新会话状态
    const updateStatus = async () => {
      try {
        const status = await apiService.getStatus()
        recordedParams.value = status.recorded_params
        missingParams.value = status.missing_params
        sessionStatus.value = status.status
      } catch (error) {
        console.error('Failed to update status:', error)
      }
    }

    const startSession = async () => {
      try {
        initializeSocket(handleBackendMessage)

        const { hasActiveSession } = getSocketState()
        if (hasActiveSession) {
          sessionStatus.value = 'processing'
          isLoading.value = false
          if (messages.value.length === 0) {
            addMessage('system', '🔄 已恢复已有会话，请继续交流')
          }
          updateStatus()
          return
        }

        isLoading.value = true
        sessionStatus.value = 'processing'
        resetStreamingState()
        messages.value = []
        persistMessages()
        
        addMessage('system', '⏳ 正在连接到 AI 助手...')
        requestSessionStart()
        updateStatus()
      } catch (error) {
        console.error('Failed to start session:', error)
        addMessage('system', `❌ 启动会话失败: ${error.message}`)
        isLoading.value = false
      }
    }

    onMounted(async () => {
      initializeSocket(handleBackendMessage)
      if (messages.value.length === 0) {
        addMessage('system', '⏳ 正在启动 AI 会话...')
      }
      await startSession()
    })

    onUnmounted(() => {
      resetStreamingState()
      if (persistTimer) {
        clearTimeout(persistTimer)
        persistTimer = null
      }
      clearMessageCallback()
    })

    return {
      messages,
      isLoading,
      inputEnabled,
      showReturnValueModal,
      sessionStatus,
      recordedParams,
      currentToolInfo,
      showDesignResult,
      designResult,
      handleSendMessage,
      handleReturnValue,
      startSession,
      updateStatus
    }
  }
}
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f6f8fb;
  padding: 20px;
}

.chat-wrapper {
  height: 95vh;
  display: flex;
  flex-direction: column;
  max-width: 1000px;
  margin: 0 auto;
  width: 100%;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}
</style>
