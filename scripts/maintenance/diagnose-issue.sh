#!/bin/bash

# Diagnose what's really happening with the API startup

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Drass API Startup Diagnosis ===${NC}"
echo "Time: $(date)"
echo "User: $(whoami)"
echo ""

# 1. Check what's on port 8888
echo -e "${BLUE}1. What's using port 8888?${NC}"
if lsof -i :8888 >/dev/null 2>&1; then
    echo -e "${RED}Port 8888 is in use:${NC}"
    lsof -i :8888
    echo ""

    # Get the PID and check what command it's running
    PID=$(lsof -ti :8888 | head -1)
    if [ -n "$PID" ]; then
        echo "Process details (PID $PID):"
        ps -fp $PID
        echo ""
        echo "Full command line:"
        cat /proc/$PID/cmdline 2>/dev/null | tr '\0' ' ' || echo "Cannot read command"
        echo -e "\n"

        # Check when it started
        echo "Process start time:"
        ps -o lstart= -p $PID
    fi
else
    echo -e "${GREEN}Port 8888 is free${NC}"
fi
echo ""

# 2. Check running Python processes
echo -e "${BLUE}2. Running Python processes:${NC}"
ps aux | grep -E "python.*uvicorn|python.*main|python.*api" | grep -v grep || echo "No relevant Python processes found"
echo ""

# 3. Check the log file
echo -e "${BLUE}3. Log file status:${NC}"
LOG_FILE="/home/qwkj/drass/logs/drass-api.log"
if [ -f "$LOG_FILE" ]; then
    echo "Log file exists"
    echo "Last modified: $(stat -c %y $LOG_FILE 2>/dev/null || stat -f "%Sm" $LOG_FILE 2>/dev/null)"
    echo "Size: $(ls -lh $LOG_FILE | awk '{print $5}')"
    echo ""
    echo "First line of log:"
    head -1 "$LOG_FILE"
    echo ""
    echo "Last timestamp in log:"
    grep -o '"timestamp": "[^"]*"' "$LOG_FILE" | tail -1
else
    echo "Log file not found"
fi
echo ""

# 4. Test if we can actually start something on port 8888
echo -e "${BLUE}4. Test port 8888 availability:${NC}"
python3 -c "
import socket
import sys

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', 8888))
    s.listen(1)
    print('✓ Successfully bound to port 8888')
    s.close()
except OSError as e:
    print(f'✗ Cannot bind to port 8888: {e}')
    sys.exit(1)
"
echo ""

# 5. Check what start-as-user.sh actually does
echo -e "${BLUE}5. What start-as-user.sh would run:${NC}"
if [ -f "/home/qwkj/drass/start-as-user.sh" ]; then
    echo "Script exists"
    echo "Looking for uvicorn command:"
    grep -n "uvicorn" /home/qwkj/drass/start-as-user.sh | head -5
else
    echo "start-as-user.sh not found!"
fi
echo ""

# 6. Check if there's a zombie process or stale PID file
echo -e "${BLUE}6. Check for stale processes:${NC}"
# Check for PID files
find /home/qwkj/drass -name "*.pid" -type f 2>/dev/null | while read pidfile; do
    echo "Found PID file: $pidfile"
    PID=$(cat "$pidfile")
    if ps -p $PID > /dev/null 2>&1; then
        echo "  Process $PID is still running"
    else
        echo "  Process $PID is NOT running (stale PID file)"
    fi
done

# Check for uvicorn.pid specifically
if [ -f "/tmp/uvicorn.pid" ]; then
    echo "Found /tmp/uvicorn.pid"
fi
echo ""

# 7. Check if the log is being appended to or overwritten
echo -e "${BLUE}7. Recent log activity:${NC}"
echo "Last 5 'Starting' entries in log (with line numbers):"
grep -n "Starting.*API\|Starting Simple API" "$LOG_FILE" 2>/dev/null | tail -5
echo ""

# 8. Recommendation
echo -e "${BLUE}=== Diagnosis Complete ===${NC}"
echo ""
echo -e "${YELLOW}Recommendations:${NC}"

if lsof -i :8888 >/dev/null 2>&1; then
    echo "1. Kill the process on port 8888:"
    echo "   kill -9 $(lsof -ti :8888 | tr '\n' ' ')"
fi

echo "2. Clear the log file to see fresh output:"
echo "   > $LOG_FILE"
echo ""
echo "3. Run with explicit logging:"
echo "   cd /home/qwkj/drass"
echo "   python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8888 2>&1 | tee fresh.log"