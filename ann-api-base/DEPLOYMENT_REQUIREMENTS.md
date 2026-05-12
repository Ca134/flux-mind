# ANN 后端部署要求

## 结论

这个 ANN 后端部署时一般不需要 GPU。模型本身很小，真正吃资源的是 `/optimize` 生成候选点、批量推理和结果缓存。

## 推荐配置

### 仅使用 `/predict`

- `2 vCPU`
- `4 GB RAM`
- `10 GB` 磁盘
- 无需 GPU

### 使用 `/optimize`，且用户输入范围通常较窄

- `4 vCPU`
- `8 GB ~ 16 GB RAM`
- `20 GB` 磁盘
- 无需 GPU

推荐环境变量：

```env
ANN_DEVICE=cpu
ANN_OPTIMIZATION_CACHE_SIZE=1
```

### 使用 `/optimize`，且可能接近默认全量搜索

- `8 vCPU`
- `32 GB RAM`
- `30 GB` 磁盘
- 无需 GPU

## 说明

- `/predict` 压力很小，CPU 部署即可。
- `/optimize` 会生成大量候选点，内存压力明显大于模型推理本身。
- 默认优化结果会缓存多份，内存小的机器建议把 `ANN_OPTIMIZATION_CACHE_SIZE` 降到 `1`。
- 建议先用单进程、单 worker 部署，避免内存被重复放大。

## 实际建议

如果这个服务要正式跑 `/optimize`，建议先按下面配置上线：

- `4 vCPU + 16 GB RAM`
- `ANN_DEVICE=cpu`
- `ANN_OPTIMIZATION_CACHE_SIZE=1`
- `uvicorn` 使用单 worker
