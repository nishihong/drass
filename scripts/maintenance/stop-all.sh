#!/bin/bash

# Comprehensive service stop and cleanup script

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

BASE_DIR="/home/qwkj/drass"

echo -e "${BLUE}======================================================${NC}"
echo -e "${BLUE}          Stopping All Drass Services${NC}"
echo -e "${BLUE}======================================================${NC}"
echo ""

# 1. Stop services by PID files
echo -e "${BLUE}1. Checking PID files...${NC}"
PID_LOCATIONS=(
    "$BASE_DIR/.running_processes"
    "$BASE_DIR/logs/*.pid"
    "$BASE_DIR/.pids/*.pid"
    "$BASE_DIR/*.pid"
)

for pattern in "${PID_LOCATIONS[@]}"; do
    for pidfile in $pattern; do
        if [ -f "$pidfile" ]; then
            PID=$(cat "$pidfile" 2>/dev/null)
            if [ -n "$PID" ] && ps -p $PID > /dev/null 2>&1; then
                echo -e "${YELLOW}  Stopping process $PID from $(basename $pidfile)${NC}"
                kill $PID 2>/dev/null
                sleep 1
                # Force kill if still running
                if ps -p $PID > /dev/null 2>&1; then
                    kill -9 $PID 2>/dev/null
                fi
            fi
            rm -f "$pidfile"
        fi
    done
done
echo -e "${GREEN}✓${NC} PID files processed"
echo ""

# 2. Stop services by port
echo -e "${BLUE}2. Stopping services by port...${NC}"
PORTS=(
    "8888:Drass API"
    "8000:Backend API"
    "8001:LLM Server"
    "8002:Embedding Service"
    "8004:Scheduler"
    "8005:Doc Processor"
    "8010:vLLM Embedding"
    "8012:vLLM Reranker"
    "5173:Frontend"
    "5174:Frontend Dev"
)

for port_info in "${PORTS[@]}"; do
    IFS=':' read -r port name <<< "$port_info"
    pids=$(lsof -ti:$port 2>/dev/null)
    if [ -n "$pids" ]; then
        echo -e "${YELLOW}  Stopping $name on port $port (PIDs: $pids)${NC}"
        echo $pids | xargs -r kill -9 2>/dev/null
    fi
done
echo -e "${GREEN}✓${NC} Port cleanup complete"
echo ""

# 3. Stop services by process name
echo -e "${BLUE}3. Stopping services by name...${NC}"
PROCESS_PATTERNS=(
    "uvicorn.*app.main"
    "uvicorn.*8888"
    "qwen3_api_server"
    "embedding-service"
    "doc-processor"
    "scheduler"
    "simple_api.py"
    "standalone_api.py"
    "simple_backend.py"
    "vite"
    "npm.*dev"
    "python.*streamlit"
)

for pattern in "${PROCESS_PATTERNS[@]}"; do
    if pgrep -f "$pattern" > /dev/null 2>&1; then
        echo -e "${YELLOW}  Stopping processes matching: $pattern${NC}"
        pkill -9 -f "$pattern" 2>/dev/null
    fi
done
echo -e "${GREEN}✓${NC} Process cleanup complete"
echo ""

# 4. Clean up stale files
echo -e "${BLUE}4. Cleaning up stale files...${NC}"
# Remove all PID files
find "$BASE_DIR" -name "*.pid" -type f -delete 2>/dev/null
rm -f "$BASE_DIR/.running_processes" 2>/dev/null

# Clean Python cache
find "$BASE_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$BASE_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true

echo -e "${GREEN}✓${NC} Cleanup complete"
echo ""

# 5. Verify all services are stopped
echo -e "${BLUE}5. Verification...${NC}"
ALL_STOPPED=true

# Check main ports
for port_info in "${PORTS[@]}"; do
    IFS=':' read -r port name <<< "$port_info"
    if lsof -i:$port > /dev/null 2>&1; then
        echo -e "${RED}  WARNING: $name still running on port $port${NC}"
        ALL_STOPPED=false
    fi
done

if [ "$ALL_STOPPED" = true ]; then
    echo -e "${GREEN}✓ All services stopped successfully!${NC}"
else
    echo -e "${YELLOW}⚠ Some services may still be running${NC}"
    echo -e "${YELLOW}  Run 'lsof -i' to check${NC}"
fi

echo ""
echo -e "${BLUE}======================================================${NC}"
echo -e "${GREEN}Service shutdown complete!${NC}"
echo -e "${BLUE}======================================================${NC}"
echo ""
echo "Next steps:"
echo "  • To start again: bash start-as-user.sh"
echo "  • To clean logs: bash cleanup-stale.sh"
echo "  • To diagnose: bash diagnose-issue.sh"