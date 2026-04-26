#!/bin/bash

# Simple frontend server for production build
# Uses Python http.server which is most reliable across different systems

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Detect the actual directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="$SCRIPT_DIR"
FRONTEND_DIR="$BASE_DIR/frontend"
LOG_DIR="$BASE_DIR/logs"

mkdir -p "$LOG_DIR"

echo -e "${BLUE}=== Starting Frontend Server ===${NC}"
echo "Date: $(date)"
echo ""

# Check if dist exists
if [ ! -d "$FRONTEND_DIR/dist" ]; then
    echo -e "${RED}ERROR: Frontend build not found at $FRONTEND_DIR/dist${NC}"
    echo "Please run: bash rebuild-frontend.sh first"
    exit 1
fi

# Stop any existing service on port 5173
if lsof -i :5173 >/dev/null 2>&1; then
    echo -e "${YELLOW}Stopping existing service on port 5173...${NC}"
    lsof -ti :5173 | xargs -r kill 2>/dev/null
    sleep 2
fi

cd "$FRONTEND_DIR/dist"

# Use Python http.server
if command -v python3 >/dev/null 2>&1; then
    echo -e "${BLUE}Starting Python http.server on port 5173...${NC}"

    # Create a Python script for better control
    cat > ../serve.py << 'EOF'
#!/usr/bin/env python3
import http.server
import socketserver
import os
import sys
from pathlib import Path

PORT = 5173
DIRECTORY = "dist"

class SPAHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        # Get the requested path
        path = self.translate_path(self.path)

        # If path doesn't exist or is a directory, serve index.html
        if not os.path.exists(path) or os.path.isdir(path):
            self.path = '/index.html'

        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def log_message(self, format, *args):
        # Reduce verbosity
        if '/assets/' not in args[0]:
            super().log_message(format, *args)

os.chdir(os.path.dirname(os.path.abspath(__file__)))

Handler = SPAHandler

with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print(f"Server running at http://0.0.0.0:{PORT}/")
    print(f"Local URL: http://localhost:{PORT}/")
    print("Press Ctrl+C to stop")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)
EOF

    cd "$FRONTEND_DIR"
    nohup python3 serve.py > "$LOG_DIR/frontend-server.log" 2>&1 &
    PID=$!

    echo "Server PID: $PID"
    echo $PID > "$LOG_DIR/frontend-server.pid"

    # Wait and check
    sleep 3

    if ps -p $PID > /dev/null; then
        echo -e "${GREEN}✓${NC} Frontend server is running"
        echo ""
        echo "Access the frontend at:"
        echo "  http://localhost:5173"
        echo ""
        echo "Server details:"
        echo "  PID: $PID"
        echo "  Log: $LOG_DIR/frontend-server.log"
        echo ""
        echo "To stop: kill $PID"
        echo "To monitor: tail -f $LOG_DIR/frontend-server.log"
    else
        echo -e "${RED}✗${NC} Failed to start server"
        tail -10 "$LOG_DIR/frontend-server.log"
        exit 1
    fi

elif command -v python >/dev/null 2>&1; then
    # Try Python 2 as last resort
    echo -e "${YELLOW}Using Python 2 (not recommended)...${NC}"
    nohup python -m SimpleHTTPServer 5173 > "$LOG_DIR/frontend-server.log" 2>&1 &
    PID=$!
    echo $PID > "$LOG_DIR/frontend-server.pid"
    sleep 3

    if ps -p $PID > /dev/null; then
        echo -e "${GREEN}✓${NC} Frontend server is running (Python 2)"
        echo "URL: http://localhost:5173"
    else
        echo -e "${RED}✗${NC} Failed to start server"
        exit 1
    fi
else
    echo -e "${RED}ERROR: Python is not installed${NC}"
    echo "Please install Python 3:"
    echo "  sudo apt-get install python3"
    exit 1
fi