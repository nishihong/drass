#!/bin/bash

# 磐石数据合规分析系统 - 前端服务启动脚本
# 优化版本，支持与VLLM后端集成

set -e

echo "🚀 启动磐石数据合规分析系统前端服务..."

# 检查Node.js环境
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装，请先安装 Node.js"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm 未安装，请先安装 npm"
    exit 1
fi

# 检查前端目录
FRONTEND_DIR="/home/qwkj/drass/frontend"
if [ ! -d "$FRONTEND_DIR" ]; then
    echo "❌ 前端目录不存在: $FRONTEND_DIR"
    exit 1
fi

cd "$FRONTEND_DIR"

# 检查package.json
if [ ! -f "package.json" ]; then
    echo "❌ package.json 不存在"
    exit 1
fi

# 检查node_modules
if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install
fi

# 检查后端服务状态
echo "🔍 检查后端服务状态..."
if curl -s "http://localhost:8888/health" > /dev/null; then
    echo "✅ 后端API服务运行正常 (端口 8888)"
else
    echo "⚠️  后端API服务未运行，请先启动后端服务"
    echo "   运行: ./start-compliance-assistant.sh"
fi

# 检查VLLM服务状态
if curl -s -H "Authorization: Bearer 123456" "http://localhost:8001/v1/models" > /dev/null; then
    echo "✅ VLLM服务运行正常 (端口 8001)"
else
    echo "⚠️  VLLM服务未运行，请先启动VLLM服务"
    echo "   运行: ./deployment/scripts/restart-vllm-optimized.sh"
fi

# 清理旧的进程
echo "🧹 清理旧的前端进程..."
pkill -f "vite.*5173" || true
pkill -f "node.*dev" || true

# 等待端口释放
sleep 2

# 检查端口5173是否被占用
if lsof -i :5173 > /dev/null 2>&1; then
    echo "❌ 端口 5173 仍被占用，请手动清理"
    lsof -i :5173
    exit 1
fi

# 设置环境变量
export NODE_ENV=development
export VITE_API_BASE_URL=http://localhost:8888/api/v1
export VITE_WS_URL=ws://localhost:8888

# 启动前端开发服务器
echo "🎨 启动前端开发服务器..."
echo "   前端地址: http://localhost:5173"
echo "   后端API: http://localhost:8888"
echo "   VLLM服务: http://localhost:8001"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

# 启动Vite开发服务器
npm run dev

