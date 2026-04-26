#!/bin/bash

# 磐石数据合规助手启动脚本
# 集成VLLM本地模型的完整启动流程

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函数定义
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 检查服务状态
check_service() {
    local service_name=$1
    local port=$2
    local url=${3:-"http://localhost:$port"}
    
    # 特殊处理VLLM服务，需要API密钥
    if [[ "$url" == *"/v1/models"* ]]; then
        if curl -sf -H "Authorization: Bearer 123456" "$url" > /dev/null 2>&1; then
            print_success "$service_name 正在运行 (端口 $port)"
            return 0
        else
            print_error "$service_name 未运行 (端口 $port)"
            return 1
        fi
    else
        if curl -sf "$url" > /dev/null 2>&1; then
            print_success "$service_name 正在运行 (端口 $port)"
            return 0
        else
            print_error "$service_name 未运行 (端口 $port)"
            return 1
        fi
    fi
}

# 启动服务
start_service() {
    local service_name=$1
    local start_command=$2
    local check_port=$3
    
    print_status "启动 $service_name..."
    
    # 在后台启动服务
    eval "$start_command" &
    local pid=$!
    
    # 等待服务启动
    local max_wait=30
    local wait_count=0
    
    while [ $wait_count -lt $max_wait ]; do
        if curl -sf "http://localhost:$check_port" > /dev/null 2>&1; then
            print_success "$service_name 启动成功 (PID: $pid)"
            return 0
        fi
        sleep 2
        wait_count=$((wait_count + 1))
        echo -n "."
    done
    
    print_error "$service_name 启动失败或超时"
    return 1
}

# 主函数
main() {
    echo "=========================================="
    echo "🚀 磐石数据合规助手启动"
    echo "=========================================="
    echo "集成VLLM本地模型的智能合规分析系统"
    echo "=========================================="

    # 检查当前目录
    if [ ! -f "package.json" ] && [ ! -f "frontend/package.json" ]; then
        print_error "请在项目根目录下运行此脚本"
        exit 1
    fi

    # 1. 检查VLLM服务状态
    print_status "检查VLLM模型服务状态..."
    
    if ! check_service "VLLM主模型服务" "8001" "http://localhost:8001/v1/models"; then
        print_warning "VLLM主模型服务未运行，请先启动VLLM服务"
        echo "启动命令示例："
        echo "  ./deployment/scripts/restart-vllm-optimized.sh"
        echo "  或者手动启动："
        echo "  vllm serve '/path/to/model' --port 8001 --api-key 123456 --served-model-name vllm"
        read -p "是否继续启动其他服务? (y/n): " continue_without_vllm
        if [ "$continue_without_vllm" != "y" ]; then
            exit 1
        fi
    fi

    # 2. 启动后端API服务
    print_status "启动后端API服务..."
    
    if ! check_service "后端API服务" "8888" "http://localhost:8888/health"; then
        # 复制环境配置文件
        if [ ! -f "services/main-app/.env" ]; then
            print_status "复制VLLM环境配置..."
            cp deployment/configs/env-ubuntu-vllm.env services/main-app/.env
        fi
        
        # 启动后端服务
        cd services/main-app
        if [ ! -d "venv" ]; then
            print_status "创建Python虚拟环境..."
            python3 -m venv venv
            source venv/bin/activate
            pip install -r requirements.txt
        else
            source venv/bin/activate
        fi
        
        # 启动API服务
        print_status "启动FastAPI服务..."
        nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8888 > ../../logs/api.log 2>&1 &
        API_PID=$!
        echo $API_PID > ../../logs/api.pid
        
        cd ../..
        
        # 等待API服务启动
        sleep 5
        if check_service "后端API服务" "8888" "http://localhost:8888/health"; then
            print_success "后端API服务启动成功 (PID: $API_PID)"
        else
            print_error "后端API服务启动失败"
            exit 1
        fi
    fi

    # 3. 启动前端服务
    print_status "启动前端服务..."
    
    if ! check_service "前端服务" "5173" "http://localhost:5173"; then
        cd frontend
        
        # 安装依赖
        if [ ! -d "node_modules" ]; then
            print_status "安装前端依赖..."
            npm install
        fi
        
        # 设置环境变量并启动开发服务器
        print_status "启动前端开发服务器..."
        export VITE_API_BASE_URL="http://localhost:8888/api/v1"
        nohup npm run dev > ../logs/frontend.log 2>&1 &
        FRONTEND_PID=$!
        echo $FRONTEND_PID > ../logs/frontend.pid
        
        cd ..
        
        # 等待前端服务启动
        sleep 10
        if check_service "前端服务" "5173" "http://localhost:5173"; then
            print_success "前端服务启动成功 (PID: $FRONTEND_PID)"
        else
            print_error "前端服务启动失败"
            exit 1
        fi
    fi

    # 4. 最终状态检查
    echo ""
    echo "=========================================="
    echo "🎉 服务状态检查"
    echo "=========================================="
    
    check_service "VLLM主模型服务" "8001" "http://localhost:8001/v1/models" || true
    check_service "后端API服务" "8888" "http://localhost:8888/health"
    check_service "前端服务" "5173" "http://localhost:5173"
    
    echo ""
    echo "=========================================="
    echo "✅ 磐石数据合规助手启动完成"
    echo "=========================================="
    echo ""
    echo "🌐 访问地址: http://localhost:5173"
    echo "📊 API文档: http://localhost:8888/docs"
    echo "🔧 健康检查: http://localhost:8888/health"
    echo ""
    echo "📝 日志文件:"
    echo "  - 后端API: logs/api.log"
    echo "  - 前端: logs/frontend.log"
    echo ""
    echo "🛑 停止服务: ./stop-all.sh"
    echo ""
    
    # 测试API连接
    print_status "测试API连接..."
    if curl -sf "http://localhost:8888/api/v1/test/services-status" > /dev/null 2>&1; then
        print_success "API连接正常"
    else
        print_warning "API连接测试失败，请检查服务状态"
    fi
    
    print_success "🎯 现在可以开始使用基于VLLM的磐石合规助手了！"
    
    # 可选：自动打开浏览器
    read -p "是否自动打开浏览器? (y/n): " open_browser
    if [ "$open_browser" = "y" ]; then
        if command -v xdg-open > /dev/null; then
            xdg-open http://localhost:5173
        elif command -v open > /dev/null; then
            open http://localhost:5173
        else
            print_status "请手动打开浏览器访问 http://localhost:5173"
        fi
    fi
}

# 创建日志目录
mkdir -p logs

# 运行主函数
main "$@"
