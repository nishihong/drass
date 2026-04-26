# 磐石数据合规分析系统 - 系统架构文档

## 📋 概述

本文档详细描述了 `bash deployment/scripts/start-ubuntu-services.sh` 启动脚本的系统架构和组件结构。

## 🏗️ 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                    磐石数据合规分析系统                          │
├─────────────────────────────────────────────────────────────────┤
│  前端层 (Frontend Layer)                                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   React/Vite    │  │   Material-UI   │  │   TypeScript    │  │
│  │   Port: 5173    │  │   Components    │  │   Frontend      │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  API网关层 (API Gateway Layer)                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   FastAPI       │  │   CORS          │  │   Authentication│  │
│  │   Port: 8888    │  │   Middleware    │  │   JWT Tokens    │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  AI服务层 (AI Services Layer)                                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   vLLM LLM      │  │   vLLM Embedding│  │   vLLM Reranking│  │
│  │   Port: 8001    │  │   Port: 8010    │  │   Port: 8012    │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  数据存储层 (Data Storage Layer)                                │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │   ChromaDB      │  │   PostgreSQL    │  │   Redis Cache   │  │
│  │   Port: 8005    │  │   Port: 5432    │  │   Port: 6379    │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 启动流程

### 1. 初始化阶段
```bash
# 配置和目录创建
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="/home/qwkj/drass"
LOG_DIR="$BASE_DIR/logs"
DATA_DIR="$BASE_DIR/data"

# 创建必要目录
mkdir -p "$LOG_DIR"
mkdir -p "$DATA_DIR/chromadb"
mkdir -p "$DATA_DIR/uploads"
```

### 2. 服务检查阶段
```bash
# 检查已运行的服务
check_existing_services() {
    # 检查端口: 5173 (前端), 8888 (API), 8005 (ChromaDB)
    # 提供重启选项: 1) 重启所有服务 2) 仅启动停止的服务 3) 取消
}
```

### 3. 服务启动阶段

#### 3.1 AI服务启动
```bash
# vLLM LLM服务 (端口 8001)
- 模型: DeepSeek-R1-0528-Qwen3-8B
- 量化: GPTQ-Int4
- GPU: AMD GPU支持
- 并行: tensor-parallel-size=2

# vLLM Embedding服务 (端口 8010)  
- 模型: Qwen3-Embedding-8B
- 任务: embed
- GPU: tensor-parallel-size=2

# vLLM Reranking服务 (端口 8012)
- 模型: Qwen3-Reranker-8B  
- 任务: embed
- GPU: tensor-parallel-size=2
```

#### 3.2 数据存储服务启动
```bash
# PostgreSQL (端口 5432)
- 数据库: langchain_db
- 用户: langchain/langchain123
- 用途: 用户数据、文档元数据

# Redis (端口 6379)
- 用途: 缓存、会话存储
- 配置: 默认配置

# ChromaDB (端口 8005)
- 用途: 向量存储
- 持久化: ./data/chromadb
- API: RESTful API
```

#### 3.3 后端API服务启动
```bash
# FastAPI后端 (端口 8888)
- 框架: FastAPI + Uvicorn
- 工作进程: 1个
- 事件循环: asyncio
- 功能: 
  * 用户认证 (JWT)
  * 文档管理
  * 聊天API
  * 知识库管理
```

#### 3.4 前端服务启动
```bash
# React前端 (端口 5173)
- 框架: React + Vite
- UI库: Material-UI
- 语言: TypeScript
- 启动方式: quick-start.sh
```

## 📊 服务依赖关系

```mermaid
graph TD
    A[前端 React] --> B[后端 FastAPI]
    B --> C[vLLM LLM服务]
    B --> D[vLLM Embedding服务]
    B --> E[vLLM Reranking服务]
    B --> F[ChromaDB向量存储]
    B --> G[PostgreSQL数据库]
    B --> H[Redis缓存]
    
    C --> I[DeepSeek-R1模型]
    D --> J[Qwen3-Embedding模型]
    E --> K[Qwen3-Reranker模型]
    
    F --> L[向量数据]
    G --> M[用户数据]
    H --> N[缓存数据]
```

## 🔧 核心功能模块

### 1. 用户认证模块
- **JWT Token管理**
- **用户注册/登录**
- **权限控制**
- **会话管理**

### 2. 文档处理模块
- **文档上传**
- **格式转换**
- **内容提取**
- **向量化处理**

### 3. 知识库管理模块
- **文档索引**
- **向量搜索**
- **相似度计算**
- **重排序优化**

### 4. 聊天对话模块
- **RAG检索增强**
- **上下文管理**
- **流式响应**
- **历史记录**

### 5. 合规分析模块
- **风险识别**
- **合规检查**
- **报告生成**
- **审计日志**

## 🌐 网络端口分配

| 服务 | 端口 | 协议 | 用途 |
|------|------|------|------|
| 前端 | 5173 | HTTP | React开发服务器 |
| 后端API | 8888 | HTTP | FastAPI应用 |
| vLLM LLM | 8001 | HTTP | 大语言模型服务 |
| vLLM Embedding | 8010 | HTTP | 嵌入向量服务 |
| vLLM Reranking | 8012 | HTTP | 重排序服务 |
| ChromaDB | 8005 | HTTP | 向量数据库 |
| PostgreSQL | 5432 | TCP | 关系数据库 |
| Redis | 6379 | TCP | 缓存数据库 |

## 📁 目录结构

```
/home/qwkj/drass/
├── deployment/scripts/          # 部署脚本
│   ├── start-ubuntu-services.sh # 主启动脚本
│   ├── stop-ubuntu-services.sh  # 停止脚本
│   └── ...
├── services/main-app/           # 后端API服务
│   ├── app/                     # FastAPI应用
│   ├── requirements.txt         # Python依赖
│   └── ...
├── frontend/                    # 前端应用
│   ├── src/                     # React源码
│   ├── package.json             # Node.js依赖
│   └── ...
├── data/                        # 数据目录
│   ├── chromadb/                # 向量数据库
│   ├── uploads/                 # 上传文件
│   └── ...
├── logs/                        # 日志目录
├── models/                      # 模型文件
└── quick-start.sh               # 快速启动脚本
```

## 🔄 启动顺序

1. **环境检查** → 检查已运行服务
2. **AI服务** → 启动vLLM服务 (LLM, Embedding, Reranking)
3. **数据存储** → 启动PostgreSQL, Redis, ChromaDB
4. **后端API** → 启动FastAPI应用
5. **前端服务** → 启动React开发服务器
6. **健康检查** → 验证所有服务状态

## 🛠️ 配置管理

### 环境变量
```bash
# LLM配置
LLM_PROVIDER=openai
OPENAI_API_BASE=http://localhost:8001/v1
LLM_MODEL=vllm

# 数据库配置
DATABASE_URL=postgresql://langchain:langchain123@localhost:5432/langchain_db
REDIS_URL=redis://localhost:6379

# 向量存储配置
VECTOR_STORE_TYPE=chromadb
CHROMA_SERVER_HOST=localhost
CHROMA_SERVER_PORT=8005
```

### 日志配置
```bash
# 日志文件位置
LOG_DIR=/home/qwkj/drass/logs/
- drass-api.log          # 后端API日志
- drass-frontend.log     # 前端日志
- vllm-llm.log          # LLM服务日志
- chromadb.log          # 向量数据库日志
```

## 🚨 故障排除

### 常见问题
1. **端口冲突** → 使用 `lsof -i :端口号` 检查
2. **服务启动失败** → 查看对应日志文件
3. **GPU内存不足** → 调整 `gpu_memory_utilization` 参数
4. **依赖缺失** → 运行 `pip install -r requirements.txt`

### 健康检查命令
```bash
# 检查所有服务状态
curl http://localhost:8888/health
curl http://localhost:8001/v1/models
curl http://localhost:8005/api/v1
curl http://localhost:5173
```

## 📈 性能优化

### GPU优化
- **tensor-parallel-size=2** → 多GPU并行
- **gpu_memory_utilization=0.45** → 内存使用率
- **max_model_len=12288** → 最大序列长度

### 缓存优化
- **Redis缓存** → 减少重复计算
- **ChromaDB持久化** → 向量数据持久存储
- **前端缓存** → 静态资源缓存

## 🔒 安全配置

### CORS配置
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 认证机制
- **JWT Token** → 无状态认证
- **密码哈希** → 安全存储
- **会话管理** → 自动过期

---

## 📞 技术支持

如有问题，请检查：
1. 日志文件: `/home/qwkj/drass/logs/`
2. 服务状态: `./manage-frontend.sh status`
3. 端口占用: `lsof -i :端口号`

**系统版本**: Ubuntu 22.04 + AMD GPU
**最后更新**: 2025-09-21
