# Flux Mind Agent 部署要求

## 结论

这个服务一般不需要 GPU。它本身不在本机跑大模型，主要负责对话编排、工具调用、知识库检索，以及转发到 ANN 后端。

## 推荐配置

### 开发或测试环境

- `2 vCPU`
- `4 GB RAM`
- `10 GB` 磁盘
- 无需 GPU

### 正式环境，低并发

- `2 ~ 4 vCPU`
- `4 GB ~ 8 GB RAM`
- `20 GB` 磁盘
- 无需 GPU

### 正式环境，多会话并发

- `4 vCPU`
- `8 GB RAM`
- `20 GB` 磁盘
- 无需 GPU

## 说明

- 这个项目不本地运行大模型，LLM 调用走外部 API。
- 优化计算不在这里执行，而是转发到独立的 ANN 后端。
- 本地知识库索引很小，磁盘和内存压力都不高。
- 主要资源消耗来自 Python 服务本身、Socket.IO 长连接和多会话状态。

## 部署前提

需要正确配置以下环境变量：

```env
ANN_API_BASE_URL=
ANN_API_KEY=
ANN_API_TIMEOUT_SECONDS=60
ANN_API_BATCH_SIZE=5000
ANN_API_RETRIES=1
SILICONFLOW_API_KEY=
SILICONFLOW_BASE_URL=
SILICONFLOW_EMBEDDING_MODEL=
```

## 实际建议

如果只是正常上线使用，建议先按下面配置部署：

- `4 vCPU + 8 GB RAM`
- 无需 GPU
- 保证能访问外部 LLM API
- 保证能访问 `ann-api-base` 服务
