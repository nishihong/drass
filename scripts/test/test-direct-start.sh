#!/bin/bash

# Test starting the API directly without any wrapper scripts

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Direct API Start Test ===${NC}"
echo "Time: $(date)"
echo "User: $(whoami)"
echo ""

# 1. First, make absolutely sure port 8888 is free
echo -e "${BLUE}Step 1: Clearing port 8888...${NC}"
if lsof -i :8888 >/dev/null 2>&1; then
    echo "Killing processes on port 8888..."
    lsof -ti :8888 | xargs -r kill -9 2>/dev/null
    sleep 2
fi

if lsof -i :8888 >/dev/null 2>&1; then
    echo -e "${RED}ERROR: Cannot clear port 8888${NC}"
    lsof -i :8888
    exit 1
fi
echo -e "${GREEN}✓${NC} Port 8888 is clear"
echo ""

# 2. Create a fresh log file
echo -e "${BLUE}Step 2: Creating fresh log...${NC}"
LOG_DIR="/home/qwkj/drass/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/test-direct-$(date +%Y%m%d-%H%M%S).log"
echo "Log file: $LOG_FILE"
echo ""

# 3. Set environment variables
echo -e "${BLUE}Step 3: Setting environment...${NC}"
export LLM_PROVIDER="openai"
export LLM_BASE_URL="http://localhost:8001/v1"
export LLM_API_KEY="123456"
export LLM_MODEL="vllm"
export MLX_ENABLED="false"
export EMBEDDING_API_BASE="http://localhost:8010/v1"
export EMBEDDING_API_KEY="123456"
export RERANKING_API_BASE="http://localhost:8012/v1"
export PORT=8888
export HOST=0.0.0.0

echo "LLM_PROVIDER=$LLM_PROVIDER"
echo "PORT=$PORT"
echo ""

# 4. Change to app directory
echo -e "${BLUE}Step 4: Changing to app directory...${NC}"
cd /home/qwkj/drass/services/main-app
echo "PWD: $(pwd)"
echo ""

# 5. Check Python
echo -e "${BLUE}Step 5: Python check...${NC}"
echo "Python: $(which python3)"
echo "Version: $(python3 --version)"

# Quick import test
echo "Testing import..."
python3 -c "from app.main import app; print('✓ Import successful')" 2>&1 | head -5
echo ""

# 6. Start the API in foreground (not background)
echo -e "${BLUE}Step 6: Starting API in FOREGROUND...${NC}"
echo "Command: python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8888"
echo "Press Ctrl+C to stop"
echo ""
echo "=== API Output ===" | tee "$LOG_FILE"

# Run in foreground so we can see exactly what happens
python3 -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8888 \
    --log-level info \
    2>&1 | tee -a "$LOG_FILE"