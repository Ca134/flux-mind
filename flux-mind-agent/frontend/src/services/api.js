// API 服务模块（仅保留获取状态接口，其他操作已改为 WebSocket）
const API_BASE_URL = '/api'

export const apiService = {
  // 获取会话状态
  async getStatus() {
    const response = await fetch(`${API_BASE_URL}/get-status`, {
      method: 'GET'
    })
    if (!response.ok) throw new Error('Failed to get status')
    return response.json()
  }
}
