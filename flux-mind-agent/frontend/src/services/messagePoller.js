/**
 * WebSocket 消息服务
 * 管理与后端的实时通信连接
 */
import { io } from 'socket.io-client'

let socket = null
let onMessageCallbackFn = null
let hasActiveSession = false
let pendingSessionStart = false

function emitToCallback(payload) {
  if (typeof onMessageCallbackFn === 'function') {
    onMessageCallbackFn(payload)
  }
}

function bindSocketListeners() {
  if (!socket) {
    return
  }

  socket.on('connect', () => {
    console.log('已连接到后端 WebSocket')
    if (pendingSessionStart && !hasActiveSession) {
      socket.emit('start_session')
      hasActiveSession = true
      pendingSessionStart = false
    }
  })

  socket.on('ai_message', (data) => {
    emitToCallback({
      type: 'ai_message',
      content: data.content
    })
  })

  socket.on('ai_message_stream', (data) => {
    emitToCallback({
      type: 'ai_message_stream',
      content: data.content,
      message_id: data.message_id,
      is_complete: data.is_complete
    })
  })

  socket.on('request_user_input', (data) => {
    emitToCallback({
      type: 'request_user_input',
      content: data.content
    })
  })

  socket.on('design_result', (data) => {
    emitToCallback({
      type: 'design_result',
      content: data.content
    })
  })

  socket.on('request_return_value', (data) => {
    emitToCallback({
      type: 'request_return_value',
      content: data.content
    })
  })

  socket.on('error', (data) => {
    emitToCallback({
      type: 'error',
      content: data.content
    })
  })

  socket.on('session_end', (data) => {
    hasActiveSession = false
    emitToCallback({
      type: 'session_end',
      content: data.content
    })
  })

  socket.on('disconnect', () => {
    console.log('与后端 WebSocket 连接已断开')
    hasActiveSession = false
  })
}

/**
 * 初始化 WebSocket 连接
 * @param {Function} onMessageCallback - 消息回调函数
 */
export function initializeSocket(onMessageCallback) {
  onMessageCallbackFn = onMessageCallback

  if (socket) {
    if (!socket.connected && !socket.active) {
      socket.connect()
    }
    return socket
  }
  
  // 根据当前访问地址自动设置后端地址
  // 如果通过 Vite 代理访问，则使用相对路径
  const backendUrl = `http://${window.location.hostname}:5000`
  
  socket = io(backendUrl, {
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionDelayMax: 5000,
    reconnectionAttempts: 5,
    timeout: 300000,        // 5分钟连接超时（支持长时间优化）
    pingTimeout: 300000,    // 5分钟心跳超时
    pingInterval: 25000     // 25秒心跳间隔
  })

  bindSocketListeners()

  return socket
}

/**
 * 启动会话
 */
export function startSession(forceRestart = false) {
  if (!socket) {
    pendingSessionStart = true
    return false
  }

  if (hasActiveSession && !forceRestart) {
    return false
  }

  pendingSessionStart = true
  if (socket.connected) {
    socket.emit('start_session')
    hasActiveSession = true
    pendingSessionStart = false
  }
  return true
}

/**
 * 发送用户输入
 * @param {string} message - 用户输入的消息
 */
export function sendUserInput(message) {
  if (socket && socket.connected) {
    socket.emit('user_input', { message })
  }
}

/**
 * 发送 return_value
 * @param {string} returnValue - 返回值
 */
export function sendReturnValue(returnValue) {
  if (socket && socket.connected) {
    socket.emit('return_value', { return_value: returnValue })
  }
}

export function clearMessageCallback() {
  onMessageCallbackFn = null
}

export function getSocketState() {
  return {
    connected: Boolean(socket && socket.connected),
    hasActiveSession
  }
}

/**
 * 关闭 WebSocket 连接
 */
export function closeSocket() {
  if (socket) {
    socket.disconnect()
    socket = null
  }
  hasActiveSession = false
  pendingSessionStart = false
}

