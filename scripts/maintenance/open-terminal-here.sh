#!/bin/bash
# 在 drass 目录下打开终端的快捷脚本

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 打开新终端并切换到 drass 目录
gnome-terminal --working-directory="$SCRIPT_DIR" -- bash -c "source venv/bin/activate; exec bash"

echo "新终端已在 $SCRIPT_DIR 目录下打开，虚拟环境已激活"
