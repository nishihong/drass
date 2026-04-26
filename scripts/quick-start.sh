#!/bin/bash

# ======================================================
# 快速启动脚本 - 重启后使用
# ======================================================
# 解决重启后前端界面变回之前状态的问题
# ======================================================

echo "🚀 启动磐石数据合规分析系统前端..."

# 检查并清理端口冲突
echo "📋 检查端口状态..."
if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  端口5173被占用，正在清理..."
    lsof -ti:5173 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# 启动前端
echo "🎯 启动前端服务..."
cd /home/qwkj/drass/frontend
nohup npm run dev > /home/qwkj/drass/logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > /home/qwkj/drass/.pids/frontend.pid

# 等待前端启动
echo "⏳ 等待前端启动..."
sleep 10

# 检查状态
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo "✅ 前端启动成功！"
    echo "🌐 访问地址: http://localhost:5173"
    echo "📊 后端API: http://localhost:8888"
    echo "📝 日志文件: /home/qwkj/drass/logs/frontend.log"
else
    echo "❌ 前端启动失败，请检查日志: /home/qwkj/drass/logs/frontend.log"
fi

echo "🎉 启动完成！"
