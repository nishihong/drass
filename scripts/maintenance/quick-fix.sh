#!/bin/bash

# ======================================================
# Quick Fix Script - Quick startup script (bypass all blocking)
# ======================================================
# Quick system startup and issue identification
# No health check waiting, all services start in parallel background
# ======================================================

set -e

# Source macOS compatibility functions
source "$(dirname "${BASH_SOURCE[0]}")/utils/macos_compat.sh" 2>/dev/null || true

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
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create necessary directories
mkdir -p "$LOG_DIR" "$PID_DIR" data/uploads data/documents data/processed models/embeddings models/reranking

# Function to print colored messages
print_status() {
    echo -e "${BLUE}[$(date +%H:%M:%S)]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[$(date +%H:%M:%S)]${NC} ✓ $1"
}

print_error() {
    echo -e "${RED}[$(date +%H:%M:%S)]${NC} ✗ $1"
}

print_warning() {
    echo -e "${YELLOW}[$(date +%H:%M:%S)]${NC} ⚠ $1"
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

# Start time tracking
START_TIME=$(date +%s)

print_section "Quick Fix Startup - $(date)"
print_warning "This script bypasses all health checks for rapid startup"
print_warning "Services may take 30-60 seconds to be fully ready"
echo

# Step 1: Quick port cleanup (parallel)
print_section "Step 1: Port Cleanup (Parallel)"
print_status "Cleaning up ports: 8001, 8000, 8002, 8004, 5173, 5003, 5432, 6379, 8005"

for port in 8001 8000 8002 8004 5173 5003 5432 6379 8005; do
    if check_port $port; then
        print_warning "Port $port in use, killing process..."
        if type kill_port &>/dev/null; then
            kill_port $port "service" &
        else
            lsof -ti:$port | xargs kill -9 2>/dev/null &
        fi
    else
        print_success "Port $port is free"
    fi
done
wait
sleep 2
print_success "All ports cleaned"

# Step 2: Check Docker (non-blocking)
print_section "Step 2: Docker Check (Non-blocking)"
if docker info > /dev/null 2>&1; then
    print_success "Docker is running"
    # Start Docker services in background
    print_status "Starting Docker services (postgres, redis, chromadb)..."
    docker-compose up -d postgres redis chromadb 2>/dev/null &
    DOCKER_PID=$!
    print_status "Docker services starting in background (PID: $DOCKER_PID)"
else
    print_warning "Docker not running - skipping Docker services"
    print_warning "Some features may be limited without PostgreSQL, Redis, and ChromaDB"
fi

# Step 3: Start all Python services (parallel, non-blocking)
print_section "Step 3: Starting All Services (Parallel)"

# 3.1 Start LLM Server
print_status "Starting LLM Server (port 8001)..."
if [ -f "$PROJECT_ROOT/qwen3_api_server.py" ]; then
    nohup python3 "$PROJECT_ROOT/qwen3_api_server.py" > "$LOG_DIR/llm_$TIMESTAMP.log" 2>&1 &
    LLM_PID=$!
    echo $LLM_PID > "$PID_DIR/llm.pid"
    print_success "LLM Server starting (PID: $LLM_PID)"
else
    print_error "qwen3_api_server.py not found"
fi

# 3.2 Start Embedding Service
print_status "Starting Embedding Service (port 8002)..."
if [ -d "$PROJECT_ROOT/services/embedding-service" ]; then
    cd "$PROJECT_ROOT/services/embedding-service"
    nohup python app.py > "$LOG_DIR/embedding_$TIMESTAMP.log" 2>&1 &
    EMBEDDING_PID=$!
    echo $EMBEDDING_PID > "$PID_DIR/embedding.pid"
    cd "$PROJECT_ROOT"
    print_success "Embedding Service starting (PID: $EMBEDDING_PID)"
else
    print_error "Embedding service directory not found"
fi

# 3.3 Start Reranking Service (if Docker available)
if docker info > /dev/null 2>&1; then
    print_status "Starting Reranking Service (port 8004)..."
    docker-compose up -d reranking-service 2>/dev/null &
    print_success "Reranking Service starting via Docker"
else
    print_warning "Reranking Service skipped (Docker not available)"
fi

# 3.4 Start Document Processor (with fallback)
print_status "Starting Document Processor (port 5003)..."
if docker info > /dev/null 2>&1; then
    # Try Docker version first
    docker-compose up -d doc-processor 2>/dev/null
    sleep 3
    # Check if Docker version is running
    if docker ps | grep -q doc-processor; then
        print_success "Document Processor starting via Docker"
    else
        print_warning "Docker doc-processor failed, starting local fallback..."
        # Start local processor as fallback
        cd "$PROJECT_ROOT/services/doc-processor"
        nohup python3 local_processor.py > "$LOG_DIR/doc-processor-local_$TIMESTAMP.log" 2>&1 &
        DOC_PROCESSOR_PID=$!
        echo $DOC_PROCESSOR_PID > "$PID_DIR/doc-processor.pid"
        cd "$PROJECT_ROOT"
        print_success "Document Processor starting locally (PID: $DOC_PROCESSOR_PID)"
    fi
else
    # No Docker, use local version directly
    print_warning "Docker not available, starting local Document Processor..."
    cd "$PROJECT_ROOT/services/doc-processor"
    nohup python3 local_processor.py > "$LOG_DIR/doc-processor-local_$TIMESTAMP.log" 2>&1 &
    DOC_PROCESSOR_PID=$!
    echo $DOC_PROCESSOR_PID > "$PID_DIR/doc-processor.pid"
    cd "$PROJECT_ROOT"
    print_success "Document Processor starting locally (PID: $DOC_PROCESSOR_PID)"
fi

# 3.5 Start Main Backend
print_status "Starting Main Backend API (port 8000)..."
if [ -d "$PROJECT_ROOT/services/main-app" ]; then
    cd "$PROJECT_ROOT/services/main-app"

    # Quick venv check/setup
    if [ ! -d "venv" ]; then
        print_status "Creating Python venv..."
        python3 -m venv venv
        source venv/bin/activate
        pip install -q -r requirements.txt 2>&1 | head -5
    else
        source venv/bin/activate
    fi

    # Set environment variables
    export LLM_BASE_URL=http://localhost:8001/v1
    export OPENAI_API_BASE=http://localhost:8001/v1
    export LLM_MODEL=qwen3-8b-mlx
    export OPENAI_API_KEY=not-required

    nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > "$LOG_DIR/backend_$TIMESTAMP.log" 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > "$PID_DIR/backend.pid"
    cd "$PROJECT_ROOT"
    print_success "Backend API starting (PID: $BACKEND_PID)"
else
    print_error "Main app directory not found"
fi

# 3.6 Start Frontend
print_status "Starting React Frontend (port 5173)..."
if [ -d "$PROJECT_ROOT/frontend" ]; then
    cd "$PROJECT_ROOT/frontend"

    # Quick npm install check
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies (this may take a minute)..."
        npm install --silent 2>&1 | head -5
    fi

    nohup npm run dev > "$LOG_DIR/frontend_$TIMESTAMP.log" 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > "$PID_DIR/frontend.pid"
    cd "$PROJECT_ROOT"
    print_success "Frontend starting (PID: $FRONTEND_PID)"
else
    print_error "Frontend directory not found"
fi

# Step 4: Quick status check (non-blocking)
print_section "Step 4: Quick Status Check"
sleep 5  # Give services a few seconds to start

# Check processes
print_status "Checking started processes..."
for service in llm embedding backend frontend; do
    if [ -f "$PID_DIR/$service.pid" ]; then
        PID=$(cat "$PID_DIR/$service.pid")
        if kill -0 $PID 2>/dev/null; then
            print_success "$service is running (PID: $PID)"
        else
            print_error "$service failed to start"
        fi
    fi
done

# Step 5: Service discovery
print_section "Step 5: Service Discovery (10s delay)"
sleep 10

print_status "Checking service availability..."
echo
echo -e "${CYAN}Service Status:${NC}"

# Check each service endpoint
services=(
    "LLM Server|8001|/health"
    "Backend API|8000|/health"
    "Frontend|5173|/"
    "Embedding|8002|/health"
    "Reranking|8004|/health"
    "Doc Processor|5003|/health"
    "ChromaDB|8005|/api/v1"
)

for service in "${services[@]}"; do
    IFS='|' read -r name port endpoint <<< "$service"
    if curl -s "http://localhost:$port$endpoint" > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} $name (port $port) - ${GREEN}AVAILABLE${NC}"
    else
        echo -e "  ${RED}✗${NC} $name (port $port) - ${YELLOW}NOT READY${NC} (may still be loading)"
    fi
done

# Step 6: Log information
print_section "Step 6: Diagnostics"

# Calculate startup time
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
print_success "Total execution time: ${DURATION} seconds"

echo
echo -e "${CYAN}📁 Log Files (timestamped):${NC}"
echo -e "  ${GREEN}•${NC} LLM:       $LOG_DIR/llm_$TIMESTAMP.log"
echo -e "  ${GREEN}•${NC} Backend:   $LOG_DIR/backend_$TIMESTAMP.log"
echo -e "  ${GREEN}•${NC} Frontend:  $LOG_DIR/frontend_$TIMESTAMP.log"
echo -e "  ${GREEN}•${NC} Embedding: $LOG_DIR/embedding_$TIMESTAMP.log"

echo
echo -e "${CYAN}🔍 Quick Diagnostics:${NC}"

# Check for common issues
echo -e "\n${YELLOW}Checking for common issues:${NC}"

# Check memory (cross-platform)
if type get_memory_gb &>/dev/null; then
    MEMORY_AVAILABLE=$(get_memory_gb)
    echo -e "  • Available Memory: ${MEMORY_AVAILABLE} GB"
    if [[ "$MEMORY_AVAILABLE" != "N/A" ]] && (( $(echo "$MEMORY_AVAILABLE < 2" | bc -l 2>/dev/null) )); then
        print_warning "Low memory detected, services may be slow to start"
    fi
else
    echo -e "  • Available Memory: Unable to detect"
fi

# Check disk space
DISK_AVAILABLE=$(df -h . | awk 'NR==2{printf "%s", $4}')
echo -e "  • Available Disk: ${DISK_AVAILABLE}"

# Check for model files
if [ -d "$PROJECT_ROOT/mlx_qwen3_converted" ]; then
    echo -e "  ${GREEN}✓${NC} MLX model found"
else
    echo -e "  ${YELLOW}⚠${NC} MLX model not found - LLM may need to download"
fi

# Check recent errors in logs
echo -e "\n${YELLOW}Recent errors in logs:${NC}"
for log in llm backend frontend embedding; do
    if [ -f "$LOG_DIR/${log}_$TIMESTAMP.log" ]; then
        ERROR_COUNT=$(grep -i "error\|exception\|failed" "$LOG_DIR/${log}_$TIMESTAMP.log" 2>/dev/null | wc -l)
        if [ $ERROR_COUNT -gt 0 ]; then
            echo -e "  ${RED}✗${NC} $log: $ERROR_COUNT errors found"
            echo "    Last error:"
            grep -i "error\|exception\|failed" "$LOG_DIR/${log}_$TIMESTAMP.log" | tail -1 | head -c 80
            echo
        else
            echo -e "  ${GREEN}✓${NC} $log: No errors detected"
        fi
    fi
done

# Final instructions
print_section "Next Steps"

echo -e "${CYAN}🎯 Commands to monitor services:${NC}"
echo -e "  ${GREEN}•${NC} Watch all logs:       tail -f $LOG_DIR/*_$TIMESTAMP.log"
echo -e "  ${GREEN}•${NC} Check specific log:   tail -f $LOG_DIR/backend_$TIMESTAMP.log"
echo -e "  ${GREEN}•${NC} Check processes:      ps aux | grep -E 'python|node|uvicorn'"
echo -e "  ${GREEN}•${NC} Check ports:          lsof -i :8000,8001,8002,8004,5173"

echo
echo -e "${CYAN}🔧 Troubleshooting:${NC}"
echo -e "  ${GREEN}•${NC} If services fail to start, check logs for detailed errors"
echo -e "  ${GREEN}•${NC} Services typically need 30-60 seconds to be fully ready"
echo -e "  ${GREEN}•${NC} Model loading may take additional time on first run"

echo
echo -e "${CYAN}🛑 To stop all services:${NC}"
echo -e "  ${GREEN}•${NC} ./stop-services.sh"

echo
print_success "Quick startup complete! Services are starting in background."
print_warning "Note: Full readiness may take 30-60 seconds."
echo

# Save diagnostic report
REPORT_FILE="$LOG_DIR/startup_report_$TIMESTAMP.txt"
{
    echo "Startup Report - $(date)"
    echo "========================="
    echo "Duration: ${DURATION} seconds"
    echo ""
    echo "Service PIDs:"
    for pid_file in "$PID_DIR"/*.pid; do
        if [ -f "$pid_file" ]; then
            service=$(basename "$pid_file" .pid)
            pid=$(cat "$pid_file")
            echo "  $service: $pid"
        fi
    done
    echo ""
    echo "Port Status:"
    for port in 8001 8000 8002 8004 5173; do
        if check_port $port; then
            echo "  $port: IN USE"
        else
            echo "  $port: FREE"
        fi
    done
} > "$REPORT_FILE"

print_success "Diagnostic report saved to: $REPORT_FILE"

exit 0