# start-ubuntu-services.sh 启动脚本详细分析

## 📋 脚本概述

`deployment/scripts/start-ubuntu-services.sh` 是磐石数据合规分析系统的主要启动脚本，负责在Ubuntu 22.04系统上启动所有必要的服务组件。

## 🏗️ 脚本结构分析

### 1. 脚本头部配置
```bash
#!/bin/bash
# Startup script for Ubuntu AMD GPU deployment
# This script starts all necessary services for Drass on Ubuntu 22.04 with AMD GPUs

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 基础配置
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="/home/qwkj/drass"
LOG_DIR="$BASE_DIR/logs"
DATA_DIR="$BASE_DIR/data"
```

### 2. 核心函数分析

#### 2.1 服务检查函数
```bash
check_existing_services() {
    # 检查端口占用情况
    # 5173: 前端服务
    # 8888: 后端API
    # 8005: ChromaDB
    
    # 提供用户选择:
    # 1) 重启所有服务
    # 2) 仅启动停止的服务  
    # 3) 取消操作
}
```

#### 2.2 服务启动函数
```bash
start_service() {
    local name=$1        # 服务名称
    local command=$2     # 启动命令
    local log_file=$3    # 日志文件
    local port=$4        # 端口号(可选)
    
    # 功能:
    # - 检查端口占用
    # - 启动服务进程
    # - 记录PID
    # - 验证启动状态
    # - 错误处理和日志记录
}
```

#### 2.3 服务状态检查函数
```bash
check_service() {
    local port=$1    # 端口号
    local name=$2    # 服务名称
    
    # 使用 lsof 检查端口监听状态
    # 返回: 0=运行中, 1=未运行
}
```

## 🚀 启动流程详解

### 阶段1: 环境准备
```bash
# 1. 创建必要目录
mkdir -p "$LOG_DIR"
mkdir -p "$DATA_DIR/chromadb"
mkdir -p "$DATA_DIR/uploads"

# 2. 检查已运行服务
check_existing_services
```

### 阶段2: AI服务启动

#### 2.1 vLLM LLM服务 (端口 8001)
```bash
# 启动命令
vllm serve /path/to/model \
    --port 8001 \
    --quantization gptq \
    --dtype float16 \
    --tensor-parallel-size 2 \
    --block-size 32 \
    --max-num-seqs 64 \
    --max-model-len 12288 \
    --gpu_memory_utilization=0.45 \
    --api_key 123456 \
    --served-model-name vllm
```

**配置说明:**
- **模型**: DeepSeek-R1-0528-Qwen3-8B
- **量化**: GPTQ-Int4 (减少显存占用)
- **并行**: 2个GPU张量并行
- **内存**: 45% GPU内存使用率
- **序列长度**: 最大12288 tokens

#### 2.2 vLLM Embedding服务 (端口 8010)
```bash
# 启动命令
python -m vllm.entrypoints.openai.api_server \
    --model /path/to/embedding/model \
    --tensor-parallel-size 2 \
    --max_model_len=8096 \
    --gpu_memory_utilization=0.3 \
    --port 8010 \
    --host 0.0.0.0 \
    --served_model_name Qwen3-Embedding-8B \
    --task embed \
    --api_key 123456
```

**配置说明:**
- **模型**: Qwen3-Embedding-8B
- **任务**: 文本嵌入
- **内存**: 30% GPU内存使用率
- **序列长度**: 最大8096 tokens

#### 2.3 vLLM Reranking服务 (端口 8012)
```bash
# 启动命令
python -m vllm.entrypoints.openai.api_server \
    --model /path/to/reranking/model \
    --tensor-parallel-size 2 \
    --max_model_len=8096 \
    --gpu_memory_utilization=0.3 \
    --port 8012 \
    --host 0.0.0.0 \
    --served_model_name Qwen3-Reranker-8B \
    --task embed \
    --api_key 123456
```

**配置说明:**
- **模型**: Qwen3-Reranker-8B
- **任务**: 文档重排序
- **内存**: 30% GPU内存使用率

### 阶段3: 数据存储服务启动

#### 3.1 PostgreSQL数据库 (端口 5432)
```bash
# 检查PostgreSQL状态
pg_isready -h localhost -p 5432

# 数据库配置
DATABASE_URL=postgresql://langchain:langchain123@localhost:5432/langchain_db
```

**用途:**
- 用户数据存储
- 文档元数据
- 系统配置
- 审计日志

#### 3.2 Redis缓存 (端口 6379)
```bash
# 检查Redis状态
redis-cli ping

# 配置
REDIS_URL=redis://localhost:6379
```

**用途:**
- 会话缓存
- 临时数据存储
- 性能优化

#### 3.3 ChromaDB向量数据库 (端口 8005)
```bash
# 启动ChromaDB
chroma run --host 0.0.0.0 --port 8005 --path ./data/chromadb
```

**用途:**
- 向量数据存储
- 相似度搜索
- 文档嵌入索引

### 阶段4: 后端API服务启动

#### 4.1 FastAPI应用 (端口 8888)
```bash
# 启动命令
cd /home/qwkj/drass/services/main-app
python3 -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8888 \
    --workers 1 \
    --loop asyncio \
    --log-level info
```

**功能模块:**
- **用户认证**: JWT Token管理
- **文档管理**: 上传、处理、索引
- **聊天API**: RAG对话接口
- **知识库**: 向量搜索和重排序
- **审计日志**: 操作记录

### 阶段5: 前端服务启动

#### 5.1 React前端 (端口 5173)
```bash
# 使用quick-start.sh启动
bash "$BASE_DIR/quick-start.sh"
```

**技术栈:**
- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **UI库**: Material-UI
- **状态管理**: Redux Toolkit
- **路由**: React Router

## 🔧 关键配置参数

### GPU配置
```bash
# LLM服务GPU配置
--tensor-parallel-size 2          # 2个GPU并行
--gpu_memory_utilization=0.45     # 45%显存使用
--max_model_len=12288             # 最大序列长度

# Embedding服务GPU配置  
--gpu_memory_utilization=0.3      # 30%显存使用
--max_model_len=8096              # 最大序列长度
```

### 网络配置
```bash
# CORS配置
allow_origins=["*"]
allow_credentials=True
allow_methods=["*"]
allow_headers=["*"]

# 代理配置
NO_PROXY="localhost,127.0.0.1,::1,0.0.0.0"
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

## 🚨 错误处理机制

### 1. 端口冲突处理
```bash
# 检查端口占用
if lsof -i :$port >/dev/null 2>&1; then
    echo "Port $port is in use"
    # 提供重启选项
fi
```

### 2. 服务启动失败处理
```bash
# 检查进程状态
if ps -p $pid > /dev/null 2>&1; then
    echo "Service started successfully"
else
    echo "Failed to start service"
    # 显示错误日志
    tail -5 "$log_file"
fi
```

### 3. 健康检查
```bash
# 服务健康检查
check_service 8001 "vLLM LLM Service"
check_service 8010 "vLLM Embedding Service"  
check_service 8012 "vLLM Reranking Service"
check_service 8888 "Drass API"
check_service 5173 "Drass Frontend"
```

## 📊 性能监控

### 资源使用监控
```bash
# GPU使用率
nvidia-smi  # NVIDIA GPU
rocm-smi    # AMD GPU

# 内存使用
free -h

# 磁盘使用
df -h

# 网络连接
netstat -tlnp
```

### 服务状态监控
```bash
# 检查所有服务端口
lsof -i :8001,8010,8012,8888,5173,5432,6379,8005

# 检查进程状态
ps aux | grep -E "(vllm|uvicorn|chroma|postgres|redis|vite)"
```

## 🔄 启动顺序依赖

```mermaid
graph TD
    A[环境检查] --> B[AI服务启动]
    B --> C[数据存储启动]
    C --> D[后端API启动]
    D --> E[前端服务启动]
    E --> F[健康检查]
    
    B1[vLLM LLM] --> B
    B2[vLLM Embedding] --> B
    B3[vLLM Reranking] --> B
    
    C1[PostgreSQL] --> C
    C2[Redis] --> C
    C3[ChromaDB] --> C
    
    D1[FastAPI] --> D
    E1[React Frontend] --> E
```

## 🛠️ 故障排除指南

### 常见问题及解决方案

#### 1. 端口冲突
```bash
# 检查端口占用
lsof -i :端口号

# 杀死占用进程
lsof -ti :端口号 | xargs kill -9
```

#### 2. GPU内存不足
```bash
# 调整GPU内存使用率
--gpu_memory_utilization=0.3  # 降低到30%

# 检查GPU状态
nvidia-smi  # 或 rocm-smi
```

#### 3. 服务启动失败
```bash
# 查看日志
tail -f /home/qwkj/drass/logs/服务名.log

# 检查依赖
pip install -r requirements.txt
npm install
```

#### 4. 数据库连接失败
```bash
# 检查PostgreSQL状态
sudo systemctl status postgresql
pg_isready -h localhost -p 5432

# 检查Redis状态
redis-cli ping
```

## 📈 优化建议

### 1. 性能优化
- **GPU并行**: 使用多GPU张量并行
- **内存优化**: 调整GPU内存使用率
- **缓存策略**: 启用Redis缓存
- **连接池**: 配置数据库连接池

### 2. 稳定性优化
- **健康检查**: 定期检查服务状态
- **自动重启**: 配置服务自动重启
- **日志轮转**: 配置日志文件轮转
- **监控告警**: 设置服务监控告警

### 3. 安全优化
- **访问控制**: 配置防火墙规则
- **认证加强**: 使用强密码和JWT
- **数据加密**: 启用数据传输加密
- **审计日志**: 记录所有操作日志

---

**文档版本**: v1.0  
**最后更新**: 2025-09-21  
**维护者**: 磐石数据合规分析系统团队
