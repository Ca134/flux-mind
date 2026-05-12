<template>
  <div class="design-result-overlay" @click.self="$emit('close')">
    <div class="design-result-modal">
      <div class="modal-header">
        <h3>优化设计结果</h3>
        <button class="close-btn" @click="$emit('close')">&times;</button>
      </div>

      <div class="modal-body">
        <!-- 摘要信息 -->
        <div v-if="result.summary" class="summary-section">
          <p>{{ result.summary }}</p>
        </div>

        <!-- 设计结果表格 -->
        <div v-if="designList && designList.length > 0" class="table-container">
          <table class="design-table">
            <thead>
              <tr>
                <th>序号</th>
                <th v-for="col in tableColumns" :key="col.key">{{ col.label }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(design, index) in designList" :key="index">
                <td>{{ index + 1 }}</td>
                <td v-for="col in tableColumns" :key="col.key">
                  {{ formatValue(design, col) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 无结果提示 -->
        <div v-else-if="result.error" class="error-message">
          {{ result.error }}
        </div>
        <div v-else class="no-result">
          暂无设计结果
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DesignResultTable',
  props: {
    result: {
      type: Object,
      default: () => ({})
    }
  },
  emits: ['close'],
  computed: {
    designList() {
      // 兼容 top_designs 和 designs 两种格式
      return this.result.top_designs || this.result.designs || []
    },
    tableColumns() {
      // 固定列配置
      return [
        { key: 'type', label: '类型' },
        { key: 'dc1', label: 'dc1', from: 'params' },
        { key: 'dc2', label: 'dc2', from: 'params' },
        { key: 'ht', label: 'ht', from: 'params' },
        { key: 'Nx', label: 'Nx', from: 'params' },
        { key: 'Ny', label: 'Ny', from: 'params' },
        { key: 'c', label: 'c', from: 'params' },
        { key: 'V', label: '体积V', from: 'performance' },
        { key: 'P', label: '损耗P', from: 'performance' },
        { key: 'L', label: '电感L', from: 'performance' }
      ]
    }
  },
  methods: {
    formatValue(design, col) {
      let value
      if (col.from === 'params') {
        value = design.params?.[col.key]
      } else if (col.from === 'performance') {
        value = design.performance?.[col.key]
      } else {
        value = design[col.key]
      }
      if (value === null || value === undefined) return '-'
      if (typeof value === 'number') {
        return Number.isInteger(value) ? value : value.toFixed(2)
      }
      return value
    }
  }
}
</script>

<style scoped>
.design-result-overlay {
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
}

.design-result-modal {
  background: white;
  border-radius: 12px;
  max-width: 90vw;
  max-height: 80vh;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.close-btn:hover {
  opacity: 0.8;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
  max-height: calc(80vh - 60px);
}

.summary-section {
  margin-bottom: 16px;
  padding: 12px;
  background: #e8f5e9;
  border-radius: 8px;
  color: #2e7d32;
}

.table-container {
  overflow-x: auto;
}

.design-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.design-table th,
.design-table td {
  padding: 10px 12px;
  text-align: center;
  border: 1px solid #e0e0e0;
}

.design-table th {
  background: #f5f5f5;
  font-weight: 600;
  color: #333;
  white-space: nowrap;
}

.design-table tbody tr:hover {
  background: #f0f7ff;
}

.design-table tbody tr:nth-child(even) {
  background: #fafafa;
}

.design-table tbody tr:nth-child(even):hover {
  background: #f0f7ff;
}

.error-message {
  padding: 20px;
  text-align: center;
  color: #d32f2f;
  background: #ffebee;
  border-radius: 8px;
}

.no-result {
  padding: 20px;
  text-align: center;
  color: #666;
}
</style>
