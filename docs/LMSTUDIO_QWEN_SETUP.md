# LM Studio Qwen 模型配置指南

## 问题说明
MLX 格式模型需要特殊的 Python 依赖，在 LM Studio 中可能会遇到兼容性问题。

## 推荐解决方案：使用 GGUF 格式

### 1. 下载 GGUF 格式的 Qwen 模型

在 LM Studio 中搜索并下载以下模型之一：

#### 推荐模型列表（按性能从高到低）：
- **Qwen/Qwen2.5-7B-Instruct-GGUF** 
  - 文件：`qwen2.5-7b-instruct-q4_k_m.gguf` (4.9GB, 平衡性能)
  - 文件：`qwen2.5-7b-instruct-q5_k_m.gguf` (5.8GB, 更高质量)
  
- **Qwen/Qwen2.5-3B-Instruct-GGUF**
  - 文件：`qwen2.5-3b-instruct-q4_k_m.gguf` (2.0GB, 快速响应)
  - 文件：`qwen2.5-3b-instruct-q5_k_m.gguf` (2.4GB, 更高质量)

- **Qwen/Qwen2.5-1.5B-Instruct-GGUF**
  - 文件：`qwen2.5-1.5b-instruct-q4_k_m.gguf` (1.0GB, 超快速度)

### 2. 在 LM Studio 中配置

1. **下载模型**：
   - 打开 LM Studio
   - 点击 "Discover" 标签
   - 搜索 "Qwen2.5 GGUF"
   - 选择合适的模型大小
   - 点击下载

2. **加载模型**：
   - 进入 "Local Server" 标签
   - 在 Model 下拉菜单中选择下载的 GGUF 模型
   - 点击 "Load Model"

3. **配置参数**（推荐设置）：
   ```yaml
   Context Length: 8192
   Temperature: 0.7
   Top P: 0.95
   GPU Layers: -1 (使用所有 GPU)
   Threads: 8 (根据你的 CPU 核心数调整)
   ```

### 3. 测试 API 连接

模型加载成功后，测试 API：

```bash
# 测试 LM Studio API
curl http://localhost:1234/v1/models

# 测试聊天功能
curl http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5-7b-instruct",
    "messages": [{"role": "user", "content": "你好"}],
    "temperature": 0.7
  }'
```

### 4. 在项目中配置

更新 `.env` 文件：

```env
# LM Studio 配置
LLM_PROVIDER=openai  # LM Studio 兼容 OpenAI API
LLM_MODEL=qwen2.5-7b-instruct
OPENAI_API_KEY=not-needed  # LM Studio 不需要 API key
OPENAI_API_BASE=http://localhost:1234/v1
```

## 性能对比

| 模型 | 大小 | 内存占用 | 速度 | 质量 |
|------|------|----------|------|------|
| Qwen2.5-7B Q5_K_M | 5.8GB | ~8GB | 中等 | 优秀 |
| Qwen2.5-7B Q4_K_M | 4.9GB | ~7GB | 较快 | 良好 |
| Qwen2.5-3B Q5_K_M | 2.4GB | ~4GB | 快速 | 良好 |
| Qwen2.5-3B Q4_K_M | 2.0GB | ~3GB | 很快 | 可接受 |
| Qwen2.5-1.5B Q4_K_M | 1.0GB | ~2GB | 极快 | 基础 |

## 常见问题

### Q: GGUF 和 MLX 格式有什么区别？
A: 
- **GGUF**: 通用格式，CPU/GPU 混合推理，兼容性最好
- **MLX**: Apple 专用格式，需要 Metal 加速，性能更优但依赖复杂

### Q: 如何选择量化版本？
A: 
- **Q5_K_M**: 5-bit 量化，质量接近原始模型
- **Q4_K_M**: 4-bit 量化，平衡性能和质量
- **Q3_K_M**: 3-bit 量化，更快但质量略低

### Q: 内存不足怎么办？
A: 
1. 选择更小的模型（3B 或 1.5B）
2. 降低 Context Length（如 4096）
3. 减少 GPU Layers 数量

## 备选方案：修复 MLX 依赖

如果仍想使用 MLX 格式，可以尝试：

1. **完全重启 LM Studio**
2. **清理缓存**：
   ```bash
   rm -rf ~/Library/Application\ Support/LM\ Studio/Cache
   rm -rf ~/Library/Application\ Support/LM\ Studio/blob_storage
   ```
3. **重新下载模型**

但强烈建议使用 GGUF 格式以获得最佳兼容性。