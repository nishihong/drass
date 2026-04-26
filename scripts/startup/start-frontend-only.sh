#!/bin/bash

# ======================================================
# 前端服务启动脚本
# ======================================================
# 专门用于启动前端服务，解决重启后前端界面变回之前状态的问题
# ======================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$PROJECT_ROOT/logs"
PID_DIR="$PROJECT_ROOT/.pids"

# Create necessary directories
mkdir -p "$LOG_DIR" "$PID_DIR"

# Function to print colored messages
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_section() {
    echo
    echo -e "${MAGENTA}========================================${NC}"
    echo -e "${MAGENTA}  $1${NC}"
    echo -e "${MAGENTA}========================================${NC}"
}

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill process on port
kill_port() {
    local port=$1
    local service=$2
    if check_port $port; then
        local pids=$(lsof -ti:$port 2>/dev/null)
        if [ ! -z "$pids" ]; then
            print_warning "Stopping existing $service on port $port (PID: $pids)"
            kill -9 $pids 2>/dev/null || true
            sleep 2
        fi
    fi
}

# Function to wait for service
wait_for_service() {
    local url=$1
    local name=$2
    local max_attempts=30
    local attempt=0
    
    print_status "Waiting for $name to be ready..."
    while [ $attempt -lt $max_attempts ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            print_success "$name is ready!"
            return 0
        fi
        sleep 2
        attempt=$((attempt + 1))
        echo -n "."
    done
    echo
    print_error "$name failed to start (timeout after 60s)"
    return 1
}

# Function to cleanup existing processes
cleanup_existing() {
    print_section "Cleaning up existing frontend processes"
    
    # Kill processes on frontend ports
    kill_port 5173 "Frontend (5173)"
    kill_port 5174 "Frontend (5174)"
    kill_port 3000 "Frontend (3000)"
    
    # Clean up PID files
    rm -f "$PID_DIR"/frontend*.pid 2>/dev/null || true
    
    print_success "Cleanup completed"
}

# Function to start frontend
start_frontend() {
    print_section "Starting React Frontend"
    
    if check_port 5173; then
        print_warning "Frontend already running on port 5173"
    else
        cd "$PROJECT_ROOT/frontend"
        
        # Install dependencies if needed
        if [ ! -d "node_modules" ]; then
            print_status "Installing frontend dependencies..."
            npm install
        fi
        
        # Start frontend
        print_status "Starting React development server on port 5173..."
        nohup npm run dev > "$LOG_DIR/frontend.log" 2>&1 &
        FRONTEND_PID=$!
        echo $FRONTEND_PID > "$PID_DIR/frontend.pid"
        
        cd "$PROJECT_ROOT"
        wait_for_service "http://localhost:5173" "Frontend"
    fi
}

# Function to test the frontend
test_frontend() {
    print_section "Testing Frontend"
    
    # Test Frontend
    print_status "Testing Frontend..."
    if curl -s "http://localhost:5173" > /dev/null 2>&1; then
        print_success "✓ Frontend is accessible"
    else
        print_warning "✗ Frontend is not accessible"
    fi
    
    # Test if backend is available
    print_status "Testing Backend API..."
    if curl -s "http://localhost:8888/health" > /dev/null 2>&1; then
        print_success "✓ Backend API is available"
    else
        print_warning "✗ Backend API is not available"
    fi
}

# Function to show final status
show_status() {
    print_section "🚀 Frontend Started Successfully!"
    
    echo
    echo -e "${CYAN}📋 Service URLs:${NC}"
    echo -e "  ${GREEN}•${NC} Frontend:          http://localhost:5173"
    echo -e "  ${GREEN}•${NC} Backend API:       http://localhost:8888"
    echo -e "  ${GREEN}•${NC} API Documentation: http://localhost:8888/docs"
    
    echo
    echo -e "${CYAN}📁 Log Files:${NC}"
    echo -e "  ${GREEN}•${NC} Frontend:  $LOG_DIR/frontend.log"
    
    echo
    echo -e "${CYAN}🎯 Quick Tests:${NC}"
    echo -e "  ${GREEN}•${NC} Frontend:  curl http://localhost:5173"
    echo -e "  ${GREEN}•${NC} Backend:   curl http://localhost:8888/health"
    
    echo
    echo -e "${YELLOW}💡 Tips:${NC}"
    echo -e "  ${GREEN}•${NC} View logs: tail -f $LOG_DIR/frontend.log"
    echo -e "  ${GREEN}•${NC} Stop frontend: kill \$(cat $PID_DIR/frontend.pid)"
    echo -e "  ${GREEN}•${NC} Restart: ./start-frontend-only.sh"
    
    echo
    echo -e "${MAGENTA}========================================${NC}"
}

# Main execution
main() {
    clear
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════╗"
    echo "║   磐石数据合规分析系统 - 前端服务启动脚本        ║"
    echo "╚══════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    # Step 1: Cleanup
    cleanup_existing
    
    # Step 2: Start frontend
    start_frontend
    
    # Step 3: Test frontend
    test_frontend
    
    # Step 4: Show status
    show_status
}

# Run main function
main
