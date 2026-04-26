#!/bin/bash

# ======================================================
# 前端服务管理脚本
# ======================================================
# 统一管理前端服务，避免多个前端服务器同时运行
# ======================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$PROJECT_ROOT/logs"
PID_DIR="$PROJECT_ROOT/.pids"

# Create directories
mkdir -p "$LOG_DIR" "$PID_DIR"

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill all frontend processes
kill_all_frontend() {
    print_status "Stopping all frontend processes..."
    
    # Kill processes on common frontend ports
    for port in 3000 5173 5174; do
        if check_port $port; then
            local pids=$(lsof -ti:$port 2>/dev/null)
            if [ ! -z "$pids" ]; then
                print_warning "Stopping process on port $port (PID: $pids)"
                kill -9 $pids 2>/dev/null || true
            fi
        fi
    done
    
    # Kill any vite processes
    pkill -f "vite" 2>/dev/null || true
    pkill -f "npm run dev" 2>/dev/null || true
    
    # Clean up PID files
    rm -f "$PID_DIR"/frontend*.pid 2>/dev/null || true
    
    sleep 2
    print_success "All frontend processes stopped"
}

# Function to start frontend
start_frontend() {
    print_status "Starting frontend service..."
    
    if check_port 5173; then
        print_warning "Frontend already running on port 5173"
        return 0
    fi
    
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
    
    # Wait for startup
    sleep 5
    
    if check_port 5173; then
        print_success "Frontend started successfully on port 5173"
        print_status "Access URL: http://localhost:5173"
    else
        print_error "Failed to start frontend"
        return 1
    fi
}

# Function to show status
show_status() {
    echo
    echo -e "${BLUE}=== Frontend Service Status ===${NC}"
    
    for port in 3000 5173 5174; do
        if check_port $port; then
            local pids=$(lsof -ti:$port 2>/dev/null)
            echo -e "  ${GREEN}✓${NC} Port $port: Active (PID: $pids)"
        else
            echo -e "  ${RED}✗${NC} Port $port: Free"
        fi
    done
    
    echo
    echo -e "${BLUE}=== Process Information ===${NC}"
    ps aux | grep -E "(vite|npm run dev)" | grep -v grep || echo "  No frontend processes found"
    
    echo
    echo -e "${BLUE}=== Access URLs ===${NC}"
    if check_port 5173; then
        echo -e "  ${GREEN}•${NC} Frontend: http://localhost:5173"
    fi
    if check_port 5174; then
        echo -e "  ${GREEN}•${NC} Frontend (Alt): http://localhost:5174"
    fi
    if check_port 3000; then
        echo -e "  ${GREEN}•${NC} Frontend (Legacy): http://localhost:3000"
    fi
}

# Function to show help
show_help() {
    echo "Frontend Service Manager"
    echo
    echo "Usage: $0 [COMMAND]"
    echo
    echo "Commands:"
    echo "  start     Start frontend service"
    echo "  stop      Stop all frontend services"
    echo "  restart   Restart frontend service"
    echo "  status    Show service status"
    echo "  help      Show this help message"
    echo
    echo "Examples:"
    echo "  $0 start    # Start frontend"
    echo "  $0 stop     # Stop all frontend processes"
    echo "  $0 restart  # Restart frontend"
    echo "  $0 status   # Check status"
}

# Main function
main() {
    case "${1:-help}" in
        start)
            kill_all_frontend
            start_frontend
            show_status
            ;;
        stop)
            kill_all_frontend
            ;;
        restart)
            kill_all_frontend
            start_frontend
            show_status
            ;;
        status)
            show_status
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
