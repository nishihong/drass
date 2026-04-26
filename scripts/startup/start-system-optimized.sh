#!/bin/bash

# 磐石数据合规分析系统 - 优化启动脚本
# 确保服务按正确顺序启动，包含依赖检查

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查端口是否被占用
check_port() {
    local port=$1
    local service_name=$2
    if ss -tlnp | grep -q ":$port "; then
        log_warning "端口 $port ($service_name) 已被占用"
        return 1
    fi
    return 0
}

# 等待服务启动
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    log_info "等待 $service_name 启动..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            log_success "$service_name 已启动"
            return 0
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    log_error "$service_name 启动超时"
    return 1
}

# 检查服务健康状态
check_service_health() {
    local url=$1
    local service_name=$2
    local auth_header=$3
    
    log_info "检查 $service_name 健康状态..."
    
    if [ -n "$auth_header" ]; then
        response=$(curl -s -H "$auth_header" "$url")
    else
        response=$(curl -s "$url")
    fi
    
    if echo "$response" | grep -q "healthy\|models\|status.*ok\|nanosecond heartbeat\|0\.[0-9]\+\.[0-9]\+"; then
        log_success "$service_name 健康检查通过"
        return 0
    else
        log_warning "$service_name 健康检查失败: $response"
        return 1
    fi
}

# 停止现有服务
stop_existing_services() {
    log_info "停止现有服务..."
    
    # 停止后端服务
    pkill -f "uvicorn.*8888" 2>/dev/null || true
    pkill -f "python.*serve_spa" 2>/dev/null || true
    
    # 停止VLLM服务
    pkill -f "vllm.*8001" 2>/dev/null || true
    pkill -f "vllm.*8010" 2>/dev/null || true
    pkill -f "vllm.*8012" 2>/dev/null || true
    
    # 停止ChromaDB
    pkill -f "chroma.*8005" 2>/dev/null || true
    
    sleep 3
    log_success "现有服务已停止"
}

# 启动ChromaDB
start_chromadb() {
    log_info "启动ChromaDB向量数据库..."
    
    if ! check_port 8005 "ChromaDB"; then
        log_warning "ChromaDB端口被占用，跳过启动"
        return 0
    fi
    
    cd /home/qwkj/drass
    mkdir -p logs data/chromadb
    
    nohup /home/qwkj/drass/venv/bin/chroma run --path /home/qwkj/drass/data/chromadb --port 8005 --host 0.0.0.0 > logs/chromadb.log 2>&1 &
    echo $! > logs/ChromaDB.pid
    
    wait_for_service "http://localhost:8005/api/v1/version" "ChromaDB"
    check_service_health "http://localhost:8005/api/v1/version" "ChromaDB"
}

# 启动LLM主模型服务
start_llm_service() {
    log_info "启动LLM主模型服务..."
    
    if ! check_port 8001 "LLM主模型"; then
        log_warning "LLM主模型端口被占用，跳过启动"
        return 0
    fi
    
    cd /home/qwkj/drass
    mkdir -p logs
    
    nohup /home/qwkj/tritonenv/bin/python3 /home/qwkj/tritonenv/bin/vllm serve /home/qwkj/.cache/modelscope/hub/models/deepseek-ai/DeepSeek-R1-0528-Qwen3-8B --port 8001 --dtype float16 --tensor-parallel-size 2 --block-size 32 --max-num-seqs 64 --max-model-len 12288 --gpu_memory_utilization=0.45 --api_key 123456 --served-model-name vllm > logs/llm-main.log 2>&1 &
    echo $! > logs/llm-main.pid
    
    wait_for_service "http://localhost:8001/v1/models" "LLM主模型"
    check_service_health "http://localhost:8001/v1/models" "LLM主模型" "Authorization: Bearer 123456"
}

# 启动嵌入服务
start_embedding_service() {
    log_info "启动嵌入服务..."
    
    if ! check_port 8010 "嵌入服务"; then
        log_warning "嵌入服务端口被占用，跳过启动"
        return 0
    fi
    
    cd /home/qwkj/drass
    mkdir -p logs
    
    nohup python -m vllm.entrypoints.openai.api_server --model /home/qwkj/.cache/modelscope/hub/models/Qwen/Qwen3-Embedding-8B --tensor-parallel-size 2 --max_model_len=8096 --gpu_memory_utilization=0.3 --port 8010 --host 0.0.0.0 --served_model_name Qwen3-Embedding-8B --task embed --api_key 123456 > logs/embedding.log 2>&1 &
    echo $! > logs/embedding.pid
    
    wait_for_service "http://localhost:8010/v1/models" "嵌入服务"
    check_service_health "http://localhost:8010/v1/models" "嵌入服务" "Authorization: Bearer 123456"
}

# 启动重排序服务
start_reranking_service() {
    log_info "启动重排序服务..."
    
    if ! check_port 8012 "重排序服务"; then
        log_warning "重排序服务端口被占用，跳过启动"
        return 0
    fi
    
    cd /home/qwkj/drass
    mkdir -p logs
    
    nohup python -m vllm.entrypoints.openai.api_server --model /home/qwkj/Qwen3-Reranker-8B --tensor-parallel-size 2 --max_model_len=8096 --gpu_memory_utilization=0.3 --port 8012 --host 0.0.0.0 --served_model_name Qwen3-Reranker-8B --task embed --api_key 123456 > logs/reranking.log 2>&1 &
    echo $! > logs/reranking.pid
    
    wait_for_service "http://localhost:8012/v1/models" "重排序服务"
    check_service_health "http://localhost:8012/v1/models" "重排序服务" "Authorization: Bearer 123456"
}

# 启动后端API服务
start_backend_service() {
    log_info "启动后端API服务..."
    
    if ! check_port 8888 "后端API"; then
        log_warning "后端API端口被占用，跳过启动"
        return 0
    fi
    
    cd /home/qwkj/drass/services/main-app
    source /home/qwkj/drass/venv/bin/activate
    
    # 确保依赖服务已启动
    log_info "检查依赖服务状态..."
    check_service_health "http://localhost:8001/v1/models" "LLM主模型" "Authorization: Bearer 123456"
    check_service_health "http://localhost:8010/v1/models" "嵌入服务" "Authorization: Bearer 123456"
    check_service_health "http://localhost:8012/v1/models" "重排序服务" "Authorization: Bearer 123456"
    
    nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8888 --workers 1 --loop asyncio --log-level info > ../../logs/backend.log 2>&1 &
    echo $! > ../../logs/drass-api.pid
    
    wait_for_service "http://localhost:8888/health" "后端API"
    check_service_health "http://localhost:8888/health" "后端API"
}

# 启动前端服务
start_frontend_service() {
    log_info "启动前端服务..."
    
    if ! check_port 5173 "前端服务"; then
        log_warning "前端服务端口被占用，跳过启动"
        return 0
    fi
    
    cd /home/qwkj/drass/frontend
    
    # 检查后端服务是否可用
    log_info "检查后端服务状态..."
    check_service_health "http://localhost:8888/health" "后端API"
    
    nohup python3 serve_spa.py > ../logs/frontend.log 2>&1 &
    echo $! > ../logs/Drass_Frontend_Python.pid
    
    wait_for_service "http://localhost:5173" "前端服务"
    log_success "前端服务已启动"
}

# 显示系统状态
show_system_status() {
    log_info "系统启动完成！"
    echo
    echo "=========================================="
    echo "磐石数据合规分析系统 - 服务状态"
    echo "=========================================="
    echo
    echo "🌐 前端服务:     http://localhost:5173"
    echo "🔧 后端API:      http://localhost:8888"
    echo "📚 API文档:      http://localhost:8888/docs"
    echo "🤖 LLM主模型:    http://localhost:8001"
    echo "🔍 嵌入服务:     http://localhost:8010"
    echo "📊 重排序服务:   http://localhost:8012"
    echo "🗄️  向量数据库:   http://localhost:8005"
    echo
    echo "📁 日志目录:     /home/qwkj/drass/logs/"
    echo "🛑 停止服务:     ./stop-all.sh"
    echo
    echo "=========================================="
}

# 主函数
main() {
    log_info "开始启动磐石数据合规分析系统..."
    
    # 停止现有服务
    stop_existing_services
    
    # 按依赖顺序启动服务
    start_chromadb
    start_llm_service
    start_embedding_service
    start_reranking_service
    start_backend_service
    start_frontend_service
    
    # 显示系统状态
    show_system_status
    
    log_success "系统启动完成！"
}

# 执行主函数
main "$@"
