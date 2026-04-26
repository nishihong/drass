#!/bin/bash

# 服务健康状态测试脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 测试函数
test_service() {
    local url=$1
    local service_name=$2
    local auth_header=$3
    
    echo -n "测试 $service_name... "
    
    if [ -n "$auth_header" ]; then
        response=$(curl -s -H "$auth_header" "$url" 2>/dev/null)
    else
        response=$(curl -s "$url" 2>/dev/null)
    fi
    
    if [ $? -eq 0 ] && [ -n "$response" ]; then
        if echo "$response" | grep -q "healthy\|models\|status.*ok\|nanosecond heartbeat\|0\.[0-9]\+\.[0-9]\+"; then
            echo -e "${GREEN}✅ 健康${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠️  响应异常: $response${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ 无法连接${NC}"
        return 1
    fi
}

echo -e "${BLUE}磐石数据合规分析系统 - 服务健康检查${NC}"
echo "=========================================="

# 测试各个服务
test_service "http://localhost:8005/api/v1/version" "ChromaDB向量数据库"
test_service "http://localhost:8001/v1/models" "LLM主模型服务" "Authorization: Bearer 123456"
test_service "http://localhost:8010/v1/models" "嵌入服务" "Authorization: Bearer 123456"
test_service "http://localhost:8012/v1/models" "重排序服务" "Authorization: Bearer 123456"
test_service "http://localhost:8888/health" "后端API服务"
test_service "http://localhost:5173" "前端服务"

echo "=========================================="
echo -e "${BLUE}健康检查完成！${NC}"
