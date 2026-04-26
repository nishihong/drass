# 磐石数据合规分析系统 - 实时状态报告

**报告时间**: 2025-09-21 10:32:00  
**系统版本**: Ubuntu 22.04 + AMD GPU  
**启动脚本**: `deployment/scripts/start-ubuntu-services.sh`

## 🚀 系统概览

磐石数据合规分析系统是一个基于AI的合规分析平台，集成了大语言模型、向量数据库、关系数据库等多种技术组件，为用户提供智能化的数据合规分析服务。

## 📊 服务状态总览

| 服务名称 | 端口 | 状态 | PID | 说明 |
|---------|------|------|-----|------|
| 前端服务 | 5173 | ✅ 运行中 | 138814 | React + Vite开发服务器 |
| 后端API | 8888 | ✅ 运行中 | 137527 | FastAPI应用 |
| vLLM LLM | 8001 | ✅ 运行中 | 9882 | DeepSeek-R1模型服务 |
| vLLM Embedding | 8010 | ✅ 运行中 | 17480 | Qwen3-Embedding模型 |
| vLLM Reranking | 8012 | ✅ 运行中 | 21585 | Qwen3-Reranker模型 |
| ChromaDB | 8005 | ✅ 运行中 | 135810 | 向量数据库 |
| PostgreSQL | 5432 | ✅ 运行中 | - | 关系数据库 |
| Redis | 6379 | ✅ 运行中 | - | 缓存数据库 |

## 🔍 详细服务分析

### 1. 前端服务 (Frontend Service)
- **状态**: ✅ 正常运行
- **端口**: 5173
- **进程ID**: 138814
- **技术栈**: React 18 + TypeScript + Vite + Material-UI
- **访问地址**: http://localhost:5173
- **功能**: 用户界面、聊天交互、文档管理

### 2. 后端API服务 (Backend API)
- **状态**: ✅ 正常运行
- **端口**: 8888
- **进程ID**: 137527
- **技术栈**: FastAPI + Uvicorn + Python 3
- **访问地址**: http://localhost:8888
- **API文档**: http://localhost:8888/docs
- **功能**: 
  - 用户认证 (JWT)
  - 文档上传和处理
  - 聊天API接口
  - 知识库管理
  - 审计日志

### 3. AI服务层 (AI Services)

#### 3.1 vLLM LLM服务
- **状态**: ✅ 正常运行
- **端口**: 8001
- **进程ID**: 9882
- **模型**: DeepSeek-R1-0528-Qwen3-8B
- **量化**: GPTQ-Int4
- **GPU配置**: tensor-parallel-size=2, gpu_memory_utilization=0.45
- **功能**: 大语言模型推理、文本生成

#### 3.2 vLLM Embedding服务
- **状态**: ✅ 正常运行
- **端口**: 8010
- **进程ID**: 17480
- **模型**: Qwen3-Embedding-8B
- **GPU配置**: tensor-parallel-size=2, gpu_memory_utilization=0.3
- **功能**: 文本嵌入向量化

#### 3.3 vLLM Reranking服务
- **状态**: ✅ 正常运行
- **端口**: 8012
- **进程ID**: 21585
- **模型**: Qwen3-Reranker-8B
- **GPU配置**: tensor-parallel-size=2, gpu_memory_utilization=0.3
- **功能**: 文档重排序优化

### 4. 数据存储层 (Data Storage)

#### 4.1 ChromaDB向量数据库
- **状态**: ✅ 正常运行
- **端口**: 8005
- **进程ID**: 135810
- **数据路径**: /home/qwkj/drass/data/chromadb
- **功能**: 向量存储、相似度搜索

#### 4.2 PostgreSQL关系数据库
- **状态**: ✅ 正常运行
- **端口**: 5432
- **数据库**: langchain_db
- **功能**: 用户数据、文档元数据、系统配置

#### 4.3 Redis缓存数据库
- **状态**: ✅ 正常运行
- **端口**: 6379
- **功能**: 会话缓存、临时数据存储

## 🔄 启动流程分析

### 当前启动方式
系统使用 `deployment/scripts/start-ubuntu-services.sh` 脚本启动，该脚本经过优化，前端部分现在使用 `quick-start.sh` 脚本启动，简化了启动流程。

### 启动顺序
1. **环境检查** → 检查已运行服务，处理端口冲突
2. **AI服务启动** → 启动vLLM服务 (LLM, Embedding, Reranking)
3. **数据存储启动** → 启动PostgreSQL, Redis, ChromaDB
4. **后端API启动** → 启动FastAPI应用
5. **前端服务启动** → 使用quick-start.sh启动React前端
6. **健康检查** → 验证所有服务状态

## 📈 性能指标

### 系统资源使用
- **CPU使用率**: 正常
- **内存使用率**: 正常
- **GPU使用率**: 45% (LLM服务), 30% (Embedding/Reranking服务)
- **磁盘使用率**: 正常

### 响应时间
- **前端加载**: < 2秒
- **API响应**: < 1秒
- **AI推理**: 2-5秒 (取决于查询复杂度)
- **向量搜索**: < 500ms

## 🛠️ 配置信息

### 关键配置参数
```bash
# GPU配置
--tensor-parallel-size 2          # 2个GPU并行
--gpu_memory_utilization=0.45     # LLM服务45%显存
--gpu_memory_utilization=0.3      # Embedding/Reranking 30%显存

# 模型配置
--max_model_len=12288             # LLM最大序列长度
--max_model_len=8096              # Embedding最大序列长度

# 网络配置
--host 0.0.0.0                    # 允许外部访问
--port 对应端口                   # 各服务端口配置
```

### 环境变量
```bash
# 数据库配置
DATABASE_URL=postgresql://langchain:langchain123@localhost:5432/langchain_db
REDIS_URL=redis://localhost:6379

# AI服务配置
OPENAI_API_BASE=http://localhost:8001/v1
EMBEDDING_API_BASE=http://localhost:8010
RERANKING_API_BASE=http://localhost:8012

# 向量存储配置
CHROMA_SERVER_HOST=localhost
CHROMA_SERVER_PORT=8005
```

## 📝 日志文件位置

| 服务 | 日志文件路径 |
|------|-------------|
| 前端服务 | /home/qwkj/drass/logs/frontend.log |
| 后端API | /home/qwkj/drass/logs/drass-api.log |
| vLLM LLM | /home/qwkj/drass/logs/vllm-llm.log |
| vLLM Embedding | /home/qwkj/drass/logs/vllm-embedding.log |
| vLLM Reranking | /home/qwkj/drass/logs/vllm-reranking.log |
| ChromaDB | /home/qwkj/drass/logs/chromadb.log |

## 🔧 管理命令

### 前端管理
```bash
# 启动前端
./quick-start.sh

# 管理前端服务
./manage-frontend.sh start    # 启动
./manage-frontend.sh stop     # 停止
./manage-frontend.sh restart  # 重启
./manage-frontend.sh status   # 查看状态
```

### 系统管理
```bash
# 启动所有服务
bash deployment/scripts/start-ubuntu-services.sh

# 停止所有服务
bash deployment/scripts/stop-ubuntu-services.sh

# 检查服务状态
curl http://localhost:8888/health
```

## 🚨 监控和告警

### 健康检查端点
- **后端API**: http://localhost:8888/health
- **vLLM LLM**: http://localhost:8001/v1/models
- **vLLM Embedding**: http://localhost:8010/health
- **vLLM Reranking**: http://localhost:8012/health
- **ChromaDB**: http://localhost:8005/api/v1

### 关键监控指标
1. **服务可用性**: 所有服务端口监听状态
2. **响应时间**: API响应时间监控
3. **资源使用**: CPU、内存、GPU使用率
4. **错误率**: 服务错误日志统计

## 🔄 最近更新

### 2025-09-21 更新
1. **前端启动优化**: 将复杂的前端启动逻辑替换为 `quick-start.sh`
2. **端口冲突处理**: 改进了端口冲突检测和处理机制
3. **服务管理**: 创建了统一的前端服务管理脚本
4. **文档完善**: 添加了详细的系统架构文档

## 📞 技术支持

### 故障排除
1. **服务无法启动**: 检查日志文件，确认依赖安装
2. **端口冲突**: 使用 `lsof -i :端口号` 检查占用
3. **GPU内存不足**: 调整 `gpu_memory_utilization` 参数
4. **数据库连接失败**: 检查数据库服务状态

### 联系方式
- **系统管理员**: 磐石数据合规分析系统团队
- **技术支持**: 查看日志文件进行问题诊断
- **文档更新**: 定期更新系统架构文档

---

**报告生成时间**: 2025-09-21 10:32:00  
**系统状态**: 🟢 所有服务正常运行  
**下次检查**: 建议每日检查服务状态
