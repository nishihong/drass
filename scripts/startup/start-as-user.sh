#!/bin/bash

# Start Drass services as regular user (not root)
# This avoids permission and virtual environment issues

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

BASE_DIR="/home/qwkj/drass"
VENV_DIR="$BASE_DIR/venv"
LOG_DIR="$BASE_DIR/logs"

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}ERROR: Do not run this script as root!${NC}"
    echo "Please run as regular user:"
    echo "  bash $0"
    echo ""
    echo "Or if you must use sudo for some services, use:"
    echo "  sudo -u qwkj bash $0"
    exit 1
fi

echo -e "${BLUE}=== Starting Drass Services (User Mode) ===${NC}"
echo "User: $(whoami)"
echo "Date: $(date)"
echo ""

# 1. Setup virtual environment if needed
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${BLUE}Setting up virtual environment...${NC}"
    python3 -m venv "$VENV_DIR"
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip

    # Install basic requirements
    pip install fastapi uvicorn httpx aiofiles
    pip install passlib[bcrypt] python-jose[cryptography]
    pip install langchain langchain-community openai

    if [ -f "$BASE_DIR/services/main-app/requirements.txt" ]; then
        pip install -r "$BASE_DIR/services/main-app/requirements.txt"
    fi
else
    echo -e "${GREEN}✓${NC} Virtual environment exists"
fi

# 2. Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source "$VENV_DIR/bin/activate"
echo "Python: $(which python)"
echo "Version: $(python --version)"

# 3. Clean up port 8888
echo -e "\n${BLUE}Checking port 8888...${NC}"
if lsof -i :8888 >/dev/null 2>&1; then
    echo -e "${YELLOW}Port 8888 is in use, cleaning up...${NC}"
    # As regular user, we can only kill our own processes
    lsof -ti :8888 | xargs -r kill 2>/dev/null
    sleep 2

    if lsof -i :8888 >/dev/null 2>&1; then
        echo -e "${RED}Cannot clean port 8888 - may need sudo${NC}"
        echo "Run: sudo lsof -ti :8888 | xargs -r kill -9"
        exit 1
    fi
fi
echo -e "${GREEN}✓${NC} Port 8888 is free"

# 4. Set environment variables
echo -e "\n${BLUE}Setting environment variables...${NC}"
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

# 5. Start the API
echo -e "\n${BLUE}Starting Drass API...${NC}"
cd "$BASE_DIR/services/main-app"

# Create log directory if needed
mkdir -p "$LOG_DIR"

# Create fresh log file
echo "=== Starting Drass API at $(date) ===" > "$LOG_DIR/drass-api.log"
echo "User: $(whoami)" >> "$LOG_DIR/drass-api.log"
echo "Python: $(which python)" >> "$LOG_DIR/drass-api.log"
echo "Working dir: $(pwd)" >> "$LOG_DIR/drass-api.log"
echo "" >> "$LOG_DIR/drass-api.log"

# Start with nohup
nohup python -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8888 \
    --workers 1 \
    --loop asyncio \
    --log-level info \
    >> "$LOG_DIR/drass-api.log" 2>&1 &

API_PID=$!
echo "API PID: $API_PID"

# Save PID
echo $API_PID > "$LOG_DIR/drass-api.pid"

# 6. Wait and check
echo -e "\n${BLUE}Waiting for API to start...${NC}"
sleep 5

if ps -p $API_PID > /dev/null; then
    echo -e "${GREEN}✓${NC} API is running (PID: $API_PID)"

    # Test the API
    echo -e "\n${BLUE}Testing API...${NC}"
    curl -s http://localhost:8888/health | head -1 && echo -e "\n${GREEN}✓${NC} API is responding" || echo -e "\n${YELLOW}API may still be starting${NC}"
else
    echo -e "${RED}✗${NC} API failed to start"
    echo "Check log: tail -50 $LOG_DIR/drass-api.log"
    exit 1
fi

echo -e "\n${BLUE}=== Startup Complete ===${NC}"
echo ""
echo "API running at: http://localhost:8888"
echo "Log file: $LOG_DIR/drass-api.log"
echo ""
echo "To stop: kill $API_PID"
echo "To check: ps -p $API_PID"
echo "To monitor: tail -f $LOG_DIR/drass-api.log"