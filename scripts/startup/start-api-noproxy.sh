#!/bin/bash

# Start API without proxy interference for local model connections
# This script bypasses proxy settings that may interfere with local vLLM connections

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Detect the actual directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="$SCRIPT_DIR"

echo -e "${BLUE}=== Starting Drass API (No Proxy) ===${NC}"
echo "User: $(whoami)"
echo "Date: $(date)"
echo "Base Directory: $BASE_DIR"
echo ""

# 1. Clean up port 8888
echo -e "${BLUE}Step 1: Ensuring port 8888 is free...${NC}"
if lsof -i :8888 >/dev/null 2>&1; then
    echo "Killing processes on port 8888..."
    lsof -ti :8888 | xargs -r kill -9 2>/dev/null
    sleep 2
fi

if lsof -i :8888 >/dev/null 2>&1; then
    echo -e "${RED}ERROR: Cannot clear port 8888${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Port 8888 is free"
echo ""

# 2. Setup Python environment
echo -e "${BLUE}Step 2: Setting up Python environment...${NC}"

# Check if venv exists
VENV_DIR="$BASE_DIR/venv"
if [ -d "$VENV_DIR" ]; then
    echo "Using existing virtual environment at $VENV_DIR"
    source "$VENV_DIR/bin/activate"
else
    echo "No virtual environment found, using system Python"
    # Try to use python3
    if command -v python3 >/dev/null 2>&1; then
        alias python=python3
    fi
fi

echo "Python: $(which python3 || which python)"
echo "Version: $(python3 --version || python --version)"
echo ""

# 3. Unset proxy variables for local connections
echo -e "${BLUE}Step 3: Clearing proxy settings...${NC}"
unset HTTP_PROXY
unset HTTPS_PROXY
unset http_proxy
unset https_proxy
unset ALL_PROXY
unset all_proxy
unset NO_PROXY
unset no_proxy
echo -e "${GREEN}✓${NC} Proxy settings cleared"
echo ""

# 4. Set environment variables for local vLLM
echo -e "${BLUE}Step 4: Setting environment variables...${NC}"
export LLM_PROVIDER="openai"
export LLM_BASE_URL="http://localhost:8001/v1"
export LLM_API_KEY="123456"
export LLM_MODEL="vllm"

# Embedding service
export EMBEDDING_API_BASE="http://localhost:8010/v1"
export EMBEDDING_API_KEY="123456"
export EMBEDDING_PROVIDER="openai"
export EMBEDDING_MODEL="embedding"

# Reranking service
export RERANKING_API_BASE="http://localhost:8012/v1"
export RERANKING_API_KEY="123456"
export RERANKING_PROVIDER="openai"
export RERANKING_ENABLED="true"

# MLX disabled for Ubuntu/AMD
export MLX_ENABLED="false"

# API settings
export PORT=8888
export HOST=0.0.0.0

# Add localhost to NO_PROXY to prevent any proxy interference
export NO_PROXY="localhost,127.0.0.1,0.0.0.0"

echo "LLM_PROVIDER=$LLM_PROVIDER"
echo "LLM_BASE_URL=$LLM_BASE_URL"
echo "NO_PROXY=$NO_PROXY"
echo ""

# 5. Check vLLM services
echo -e "${BLUE}Step 5: Checking vLLM services...${NC}"
for port_info in "8001:LLM" "8010:Embedding" "8012:Reranking"; do
    IFS=':' read -r port name <<< "$port_info"
    if lsof -i :$port >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $name service is running on port $port"
    else
        echo -e "${YELLOW}⚠${NC} $name service not detected on port $port"
    fi
done
echo ""

# 6. Start the API
echo -e "${BLUE}Step 6: Starting Drass API...${NC}"
cd "$BASE_DIR/services/main-app"

LOG_DIR="$BASE_DIR/logs"
mkdir -p "$LOG_DIR"

LOG_FILE="$LOG_DIR/drass-api-$(date +%Y%m%d-%H%M%S).log"
echo "Log file: $LOG_FILE"
echo ""

# Create startup marker
echo "=== Starting Drass API at $(date) ===" > "$LOG_FILE"
echo "User: $(whoami)" >> "$LOG_FILE"
echo "Python: $(which python3 || which python)" >> "$LOG_FILE"
echo "Working dir: $(pwd)" >> "$LOG_FILE"
echo "NO_PROXY: $NO_PROXY" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Start with nohup
echo "Starting API server..."
nohup python3 -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8888 \
    --workers 1 \
    --loop asyncio \
    --log-level info \
    >> "$LOG_FILE" 2>&1 &

API_PID=$!
echo "API PID: $API_PID"

# Save PID
echo $API_PID > "$LOG_DIR/drass-api.pid"

# 7. Wait and check
echo -e "\n${BLUE}Waiting for API to start...${NC}"
sleep 5

if ps -p $API_PID > /dev/null; then
    echo -e "${GREEN}✓${NC} API process is running (PID: $API_PID)"

    # Check if it's actually listening
    if lsof -i :8888 >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} API is listening on port 8888"

        # Test the API
        echo -e "\n${BLUE}Testing API...${NC}"
        curl -s http://localhost:8888/health | head -1 && echo -e "\n${GREEN}✓${NC} API is responding" || echo -e "\n${YELLOW}API may still be starting${NC}"
    else
        echo -e "${YELLOW}⚠${NC} API process running but not listening on port 8888 yet"
        echo "Check log: tail -50 $LOG_FILE"
    fi
else
    echo -e "${RED}✗${NC} API failed to start"
    echo "Checking log for errors..."
    echo ""
    tail -20 "$LOG_FILE"
    exit 1
fi

echo -e "\n${BLUE}=== Startup Complete ===${NC}"
echo ""
echo "API URL: http://localhost:8888"
echo "Swagger UI: http://localhost:8888/docs"
echo "Log file: $LOG_FILE"
echo ""
echo "Commands:"
echo "  Monitor log: tail -f $LOG_FILE"
echo "  Stop API: kill $API_PID"
echo "  Check status: ps -p $API_PID"
echo ""
echo "If you encounter proxy-related errors, this script has already cleared proxy settings."
echo "The API is configured to bypass proxy for local vLLM connections."