#!/bin/bash

echo "🔧 强制清理磐石数据合规系统前端缓存..."

cd /home/qwkj/drass/frontend

# 停止开发服务器（如果正在运行）
echo "⏹️  停止开发服务器..."
pkill -f "vite" 2>/dev/null || true
pkill -f "npm run dev" 2>/dev/null || true

# 清理所有缓存目录
echo "🗑️  清理缓存目录..."
rm -rf node_modules/.cache
rm -rf node_modules/.vite
rm -rf .vite
rm -rf dist
rm -rf build

# 清理 npm 缓存
echo "🧹 清理 npm 缓存..."
npm cache clean --force

# 重新安装依赖
echo "📦 重新安装依赖..."
npm install

# 重新构建
echo "🔨 重新构建项目..."
npm run build

echo "✅ 缓存清理完成！"
echo ""
echo "🚀 现在请运行以下命令启动开发服务器："
echo "   cd /home/qwkj/drass/frontend"
echo "   npm run dev"
echo ""
echo "然后在浏览器中："
echo "1. 按 Ctrl+Shift+R 强制刷新"
echo "2. 或者按 F12 打开开发者工具，右键刷新按钮，选择'清空缓存并硬性重新加载'"
