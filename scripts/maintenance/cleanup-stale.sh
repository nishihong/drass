#!/bin/bash

# Clean up stale PID files and prepare for fresh start

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

BASE_DIR="/home/qwkj/drass"

echo -e "${BLUE}=== Cleaning Up Stale Files ===${NC}"
echo ""

# 1. Clean up stale PID files
echo -e "${BLUE}Removing stale PID files...${NC}"

PID_DIRS=(
    "$BASE_DIR"
    "$BASE_DIR/logs"
    "$BASE_DIR/.pids"
)

for dir in "${PID_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        find "$dir" -maxdepth 1 -name "*.pid" -type f 2>/dev/null | while read pidfile; do
            PID=$(cat "$pidfile" 2>/dev/null)
            if [ -n "$PID" ]; then
                if ! ps -p $PID > /dev/null 2>&1; then
                    echo "  Removing stale: $pidfile (PID $PID not running)"
                    rm -f "$pidfile"
                else
                    echo "  Keeping active: $pidfile (PID $PID is running)"
                fi
            else
                echo "  Removing empty: $pidfile"
                rm -f "$pidfile"
            fi
        done
    fi
done

echo -e "${GREEN}✓${NC} PID files cleaned"
echo ""

# 2. Create fresh log directory
echo -e "${BLUE}Preparing log directory...${NC}"
mkdir -p "$BASE_DIR/logs"
chown -R $(whoami):$(whoami) "$BASE_DIR/logs" 2>/dev/null || true
echo -e "${GREEN}✓${NC} Log directory ready"
echo ""

# 3. Clear old logs (optional, keep backups)
echo -e "${BLUE}Managing log files...${NC}"
if [ -f "$BASE_DIR/logs/drass-api.log" ]; then
    # Backup old log with timestamp
    BACKUP_NAME="$BASE_DIR/logs/drass-api-$(date +%Y%m%d-%H%M%S).log.bak"
    mv "$BASE_DIR/logs/drass-api.log" "$BACKUP_NAME"
    echo "  Backed up old log to: $(basename $BACKUP_NAME)"
fi
echo -e "${GREEN}✓${NC} Logs prepared"
echo ""

# 4. Check and clean ports
echo -e "${BLUE}Checking ports...${NC}"
PORTS=(8888 8000 5173)
for port in "${PORTS[@]}"; do
    if lsof -i :$port >/dev/null 2>&1; then
        echo -e "${YELLOW}  Port $port is in use${NC}"
    else
        echo -e "${GREEN}  ✓ Port $port is free${NC}"
    fi
done
echo ""

# 5. Clean up Python cache
echo -e "${BLUE}Cleaning Python cache...${NC}"
find "$BASE_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$BASE_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true
echo -e "${GREEN}✓${NC} Python cache cleaned"
echo ""

echo -e "${BLUE}=== Cleanup Complete ===${NC}"
echo ""
echo "System is ready for a fresh start!"
echo "Next step: bash start-as-user.sh"