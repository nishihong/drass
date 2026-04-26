#!/bin/bash

# ======================================================
# LangChain System - Complete Startup Script
# ======================================================
# Complete system startup with all services including:
# - Local LLM (Qwen3-8B-MLX)
# - Embedding Service
# - Reranking Service  
# - Document Processor
# - Main Backend API
# - React Frontend
# - Vector Store (ChromaDB)
# - Database (PostgreSQL)
# - Cache (Redis)
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
DOCKER_COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"
LOG_DIR="$PROJECT_ROOT/logs"
PID_DIR="$PROJECT_ROOT/.pids"

# Create necessary directories
mkdir -p "$LOG_DIR" "$PID_DIR" data/uploads data/documents data/processed models/embeddings models/reranking

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
    print_section "Cleaning up existing processes"
    
    # Kill processes on known ports
    kill_port 8001 "LLM Server"
    kill_port 8000 "Backend API"
    kill_port 5173 "Frontend"
    kill_port 8002 "Embedding Service"
    kill_port 8004 "Reranking Service"
    kill_port 5003 "Document Processor"
    kill_port 8005 "ChromaDB"
    kill_port 5432 "PostgreSQL"
    kill_port 6379 "Redis"
    
    # Stop any existing Docker containers
    if docker-compose -f "$DOCKER_COMPOSE_FILE" ps -q 2>/dev/null | grep -q .; then
        print_warning "Stopping existing Docker containers..."
        docker-compose -f "$DOCKER_COMPOSE_FILE" down 2>/dev/null || true
    fi
    
    # Clean up PID files
    rm -f "$PID_DIR"/*.pid 2>/dev/null || true
    
    print_success "Cleanup completed"
}

# Function to setup environment
setup_environment() {
    print_section "Setting up environment"
    
    # Create .env file if it doesn't exist
    if [ ! -f "$ENV_FILE" ]; then
        print_status "Creating .env file..."
        cat > "$ENV_FILE" << 'EOF'
# LLM Configuration (Local MLX Server)
LLM_PROVIDER=openai
OPENAI_API_BASE=http://localhost:8001/v1
OPENAI_API_KEY=not-required
LLM_MODEL=qwen3-8b-mlx

# Embedding Service
EMBEDDING_PROVIDER=local
EMBEDDING_API_BASE=http://localhost:8002
EMBEDDING_MODEL=BAAI/bge-base-en-v1.5

# Reranking Service
RERANKING_ENABLED=true
RERANKING_API_BASE=http://localhost:8004
RERANKING_MODEL=BAAI/bge-reranker-base

# Vector Store
VECTOR_STORE_TYPE=chromadb
CHROMA_SERVER_HOST=localhost
CHROMA_SERVER_PORT=8005
CHROMA_PERSIST_DIRECTORY=./data/chroma

# Database
DATABASE_URL=postgresql://langchain:langchain123@localhost:5432/langchain_db
REDIS_URL=redis://localhost:6379

# Document Processing
MAX_FILE_SIZE_MB=50
ALLOWED_FILE_TYPES=pdf,docx,xlsx,pptx,txt,md,csv

# Security
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-change-in-production
JWT_ALGORITHM=HS256

# Features
ENABLE_STREAMING=true
ENABLE_AGENT=true
ENABLE_MEMORY=true
ENABLE_RERANKING=true

# Paths
UPLOAD_PATH=./data/uploads
DOCUMENT_PATH=./data/documents
PROCESSED_PATH=./data/processed
EOF
        print_success ".env file created"
    else
        print_success ".env file already exists"
    fi
    
    # Load environment variables (skip comments and empty lines)
    set -a
    source <(grep -v '^#' "$ENV_FILE" | grep -v '^$')
    set +a
}

# Function to start infrastructure services
start_infrastructure() {
    print_section "Starting infrastructure services"

    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        print_warning "Docker is not running. Attempting to start Docker Desktop..."

        # Try to start Docker on macOS
        if [[ "$OSTYPE" == "darwin"* ]]; then
            open -a Docker 2>/dev/null || true
            print_status "Waiting for Docker to start (up to 30 seconds)..."

            # Wait for Docker to be ready
            local docker_attempts=0
            while [ $docker_attempts -lt 15 ]; do
                if docker info > /dev/null 2>&1; then
                    print_success "Docker started successfully!"
                    break
                fi
                sleep 2
                docker_attempts=$((docker_attempts + 1))
                echo -n "."
            done
            echo

            # Check again if Docker is running
            if ! docker info > /dev/null 2>&1; then
                print_warning "Docker failed to start. Skipping Docker-based services."
                print_warning "Some features may be limited without PostgreSQL, Redis, and ChromaDB."
                return 0
            fi
        else
            print_warning "Docker is not running. Please start Docker manually."
            print_warning "Some features may be limited without PostgreSQL, Redis, and ChromaDB."
            return 0
        fi
    fi
    
    # Start PostgreSQL
    print_status "Starting PostgreSQL..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d postgres
    # PostgreSQL doesn't have an HTTP endpoint, just wait a few seconds for it to start
    sleep 5
    print_success "PostgreSQL started"
    
    # Start Redis
    print_status "Starting Redis..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d redis
    sleep 3
    
    # Start ChromaDB
    print_status "Starting ChromaDB Vector Store..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d chromadb
    wait_for_service "http://localhost:8005/api/v1" "ChromaDB"
    
    print_success "Infrastructure services started"
}

# Function to start microservices
start_microservices() {
    print_section "Starting microservices"
    
    # Start Embedding Service
    print_status "Starting Embedding Service..."
    if [ -d "services/embedding-service" ]; then
        cd services/embedding-service
        
        # First, upgrade sentence-transformers if needed (silent)
        pip install --upgrade sentence-transformers huggingface-hub >/dev/null 2>&1
        
        # Start the service with environment variables
        print_status "Starting embedding service on port 8002..."
        export EMBEDDING_API_BASE=http://localhost:8002
        nohup python app.py > "$LOG_DIR/embedding.log" 2>&1 &
        EMBEDDING_PID=$!
        echo $EMBEDDING_PID > "$PID_DIR/embedding.pid"
        
        cd "$PROJECT_ROOT"
        wait_for_service "http://localhost:8002/health" "Embedding Service"
    else
        print_warning "Embedding service directory not found, skipping..."
    fi
    
    # Start Reranking Service (Docker required)
    if docker info > /dev/null 2>&1; then
        print_status "Starting Reranking Service..."
        if [ -d "services/reranking-service" ]; then
            docker-compose -f "$DOCKER_COMPOSE_FILE" up -d reranking-service
            wait_for_service "http://localhost:8004/health" "Reranking Service"
        else
            print_warning "Reranking service directory not found, skipping..."
        fi
        
        # Start Document Processor
        print_status "Starting Document Processor..."
        if [ -d "services/doc-processor" ]; then
            docker-compose -f "$DOCKER_COMPOSE_FILE" up -d doc-processor
            wait_for_service "http://localhost:5003/health" "Document Processor"
        else
            print_warning "Document processor directory not found, skipping..."
        fi
    else
        print_warning "Docker not running, skipping reranking and document processor services"
    fi
    
    print_success "Microservices started"
}

# Function to start local LLM
start_llm() {
    print_section "Starting Local LLM Server"
    
    if check_port 8001; then
        print_warning "LLM server already running on port 8001"
    else
        # Check for qwen3_api_server.py
        if [ -f "$PROJECT_ROOT/qwen3_api_server.py" ]; then
            print_status "Starting Qwen3-8B-MLX server..."
            nohup python3 "$PROJECT_ROOT/qwen3_api_server.py" > "$LOG_DIR/llm.log" 2>&1 &
            LLM_PID=$!
            echo $LLM_PID > "$PID_DIR/llm.pid"
            wait_for_service "http://localhost:8001/health" "LLM Server"
        else
            print_warning "qwen3_api_server.py not found, please ensure LLM is available"
        fi
    fi
}

# Function to start main backend
start_backend() {
    print_section "Starting Main Backend API"
    
    if check_port 8000; then
        print_warning "Backend already running on port 8000"
    else
        cd "$PROJECT_ROOT/services/main-app"
        
        # Create and setup venv if needed
        if [ ! -d "venv" ]; then
            print_status "Creating Python virtual environment..."
            python3 -m venv venv
        fi
        
        # Activate venv and install dependencies
        source venv/bin/activate
        print_status "Installing dependencies in venv..."
        pip install -q -r requirements.txt 2>&1 | grep -v "Requirement already satisfied" || true
        
        # Start the main app with environment variables
        print_status "Starting FastAPI backend..."
        # Ensure environment variables are exported for the backend
        export LLM_BASE_URL=http://localhost:8001/v1
        export OPENAI_API_BASE=http://localhost:8001/v1
        export LLM_MODEL=qwen3-8b-mlx
        export OPENAI_API_KEY=not-required
        nohup uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > "$LOG_DIR/backend.log" 2>&1 &
        BACKEND_PID=$!
        echo $BACKEND_PID > "$PID_DIR/backend.pid"
        
        cd "$PROJECT_ROOT"
        wait_for_service "http://localhost:8000/health" "Backend API"
    fi
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
        print_status "Starting React development server..."
        nohup npm run dev > "$LOG_DIR/frontend.log" 2>&1 &
        FRONTEND_PID=$!
        echo $FRONTEND_PID > "$PID_DIR/frontend.pid"
        
        cd "$PROJECT_ROOT"
        # Frontend may run on port 3000 or 5173 depending on Vite config
        wait_for_service "http://localhost:3000" "Frontend" || wait_for_service "http://localhost:5173" "Frontend"
    fi
}

# Function to test the system
test_system() {
    print_section "Testing System Components"
    
    # Test LLM
    print_status "Testing LLM Server..."
    if curl -s "http://localhost:8001/health" | grep -q "healthy"; then
        print_success "✓ LLM Server is healthy"
    else
        print_warning "✗ LLM Server health check failed"
    fi
    
    # Test Backend
    print_status "Testing Backend API..."
    if curl -s "http://localhost:8000/health" | grep -q "healthy"; then
        print_success "✓ Backend API is healthy"
    else
        print_warning "✗ Backend API health check failed"
    fi
    
    # Test document upload endpoint
    print_status "Testing document upload endpoint..."
    if curl -s "http://localhost:8000/api/v1/documents" -H "Authorization: Bearer test" | grep -q "detail"; then
        print_success "✓ Document API is accessible (auth required)"
    else
        print_warning "✗ Document API test failed"
    fi
    
    # Test embedding service
    print_status "Testing Embedding Service..."
    if curl -s "http://localhost:8002/health" | grep -q "healthy"; then
        print_success "✓ Embedding Service is healthy"
    else
        print_warning "✗ Embedding Service not available"
    fi
    
    # Test vector store
    print_status "Testing ChromaDB..."
    if curl -s "http://localhost:8005/api/v1" > /dev/null 2>&1; then
        print_success "✓ ChromaDB is running"
    else
        print_warning "✗ ChromaDB not available"
    fi
}

# Function to show final status
show_status() {
    print_section "🚀 System Started Successfully!"
    
    echo
    echo -e "${CYAN}📋 Service URLs:${NC}"
    echo -e "  ${GREEN}•${NC} Frontend:          http://localhost:3000"
    echo -e "  ${GREEN}•${NC} Backend API:       http://localhost:8000"
    echo -e "  ${GREEN}•${NC} API Documentation: http://localhost:8000/docs"
    echo -e "  ${GREEN}•${NC} LLM Server:        http://localhost:8001"
    echo -e "  ${GREEN}•${NC} Embedding Service: http://localhost:8002"
    echo -e "  ${GREEN}•${NC} ChromaDB:          http://localhost:8005"
    
    echo
    echo -e "${CYAN}📁 Log Files:${NC}"
    echo -e "  ${GREEN}•${NC} LLM:      $LOG_DIR/llm.log"
    echo -e "  ${GREEN}•${NC} Backend:  $LOG_DIR/backend.log"
    echo -e "  ${GREEN}•${NC} Frontend: $LOG_DIR/frontend.log"
    
    echo
    echo -e "${CYAN}🎯 Quick Tests:${NC}"
    echo -e "  ${GREEN}•${NC} Health Check: curl http://localhost:8000/health"
    echo -e "  ${GREEN}•${NC} Upload File:  Use the UI at http://localhost:3000"
    
    echo
    echo -e "${YELLOW}💡 Tips:${NC}"
    echo -e "  ${GREEN}•${NC} To upload files for knowledge base: Select 'knowledge_base' purpose in UI"
    echo -e "  ${GREEN}•${NC} To upload files for context: Select 'business_context' purpose in UI"
    echo -e "  ${GREEN}•${NC} View logs: tail -f $LOG_DIR/<service>.log"
    echo -e "  ${GREEN}•${NC} Stop all: ./stop-services.sh"
    
    echo
    echo -e "${MAGENTA}========================================${NC}"
}

# Main execution
main() {
# clear
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════╗"
    echo "║   LangChain Compliance Assistant - Full System  ║"
    echo "╚══════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    # Step 1: Cleanup
    cleanup_existing
    
    # Step 2: Setup environment
    setup_environment
    
    # Step 3: Start infrastructure
    start_infrastructure
    
    # Step 4: Start microservices
    start_microservices
    
    # Step 5: Start LLM
    start_llm
    
    # Step 6: Start backend
    start_backend
    
    # Step 7: Start frontend
    start_frontend
    
    # Step 8: Test system
    test_system
    
    # Step 9: Show status
    show_status
}

# Run main function
main