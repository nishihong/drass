#!/bin/bash

# Clean and reinitialize the vector store database
# This fixes "no such column: collections.topic" error

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Detect the actual directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="$SCRIPT_DIR"

echo -e "${BLUE}=== Vector Store Cleanup ===${NC}"
echo "Date: $(date)"
echo "Base Directory: $BASE_DIR"
echo ""

# 1. Stop any running API services
echo -e "${BLUE}Step 1: Stopping API services...${NC}"
if [ -f "$BASE_DIR/logs/drass-api.pid" ]; then
    PID=$(cat "$BASE_DIR/logs/drass-api.pid")
    if ps -p $PID > /dev/null 2>&1; then
        echo "Stopping API service (PID: $PID)..."
        kill $PID 2>/dev/null
        sleep 2
    fi
fi
echo -e "${GREEN}✓${NC} API services stopped"
echo ""

# 2. Clean up ChromaDB data
echo -e "${BLUE}Step 2: Cleaning ChromaDB data...${NC}"

# Default ChromaDB locations
CHROMA_DIRS=(
    "$BASE_DIR/data/chroma"
    "$BASE_DIR/services/main-app/data/chroma"
    "$BASE_DIR/.chroma"
    "$HOME/.cache/chroma"
    "/tmp/chroma"
)

for dir in "${CHROMA_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "Found ChromaDB data at: $dir"
        echo -n "Removing... "
        rm -rf "$dir"
        echo -e "${GREEN}Done${NC}"
    fi
done

# Also check for SQLite database files
find "$BASE_DIR" -name "*.db" -o -name "*.sqlite" -o -name "*.sqlite3" 2>/dev/null | while read dbfile; do
    if [[ "$dbfile" == *chroma* ]]; then
        echo "Found ChromaDB database: $dbfile"
        echo -n "Removing... "
        rm -f "$dbfile"
        echo -e "${GREEN}Done${NC}"
    fi
done

echo -e "${GREEN}✓${NC} ChromaDB data cleaned"
echo ""

# 3. Create fresh data directory
echo -e "${BLUE}Step 3: Creating fresh data directory...${NC}"
mkdir -p "$BASE_DIR/data/chroma"
chmod 755 "$BASE_DIR/data"
chmod 755 "$BASE_DIR/data/chroma"
echo -e "${GREEN}✓${NC} Fresh data directory created"
echo ""

# 4. Update vector store configuration
echo -e "${BLUE}Step 4: Checking vector store configuration...${NC}"
ENV_FILE="$BASE_DIR/.env"
if [ -f "$ENV_FILE" ]; then
    # Ensure proper ChromaDB settings
    if ! grep -q "CHROMA_PERSIST_DIRECTORY" "$ENV_FILE"; then
        echo "CHROMA_PERSIST_DIRECTORY=$BASE_DIR/data/chroma" >> "$ENV_FILE"
        echo "Added CHROMA_PERSIST_DIRECTORY to .env"
    fi

    if ! grep -q "VECTOR_STORE_TYPE" "$ENV_FILE"; then
        echo "VECTOR_STORE_TYPE=chromadb" >> "$ENV_FILE"
        echo "Added VECTOR_STORE_TYPE to .env"
    fi
else
    echo "Creating .env file with vector store settings..."
    cat > "$ENV_FILE" << EOF
# Vector Store Configuration
VECTOR_STORE_TYPE=chromadb
CHROMA_PERSIST_DIRECTORY=$BASE_DIR/data/chroma

# LLM Configuration (local vLLM)
LLM_PROVIDER=openai
LLM_BASE_URL=http://localhost:8001/v1
LLM_API_KEY=123456
LLM_MODEL=vllm

# Embedding Service
EMBEDDING_API_BASE=http://localhost:8010/v1
EMBEDDING_API_KEY=123456
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=embedding

# Reranking Service
RERANKING_API_BASE=http://localhost:8012/v1
RERANKING_API_KEY=123456
RERANKING_PROVIDER=openai
RERANKING_ENABLED=true

# Disable MLX for Ubuntu/AMD
MLX_ENABLED=false
EOF
    echo -e "${GREEN}✓${NC} Created .env file"
fi
echo ""

# 5. Test import and provide fix if needed
echo -e "${BLUE}Step 5: Testing ChromaDB import...${NC}"

# Check if we have venv
if [ -d "$BASE_DIR/venv" ]; then
    source "$BASE_DIR/venv/bin/activate"
fi

python3 << EOF
import sys
try:
    import chromadb
    print("✓ ChromaDB import successful")
    print(f"  Version: {chromadb.__version__}")

    # Try to create a test client
    client = chromadb.PersistentClient(path="/tmp/test_chroma")
    print("✓ ChromaDB client creation successful")

    # Clean up test
    import shutil
    shutil.rmtree("/tmp/test_chroma", ignore_errors=True)

except ImportError as e:
    print(f"✗ ChromaDB not installed: {e}")
    print("\nTo fix, run:")
    print("  pip install chromadb")
    sys.exit(1)
except Exception as e:
    print(f"✗ ChromaDB error: {e}")
    print("\nTry reinstalling ChromaDB:")
    print("  pip uninstall chromadb -y")
    print("  pip install chromadb")
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    echo ""
    echo -e "${YELLOW}ChromaDB needs to be installed or reinstalled${NC}"
    echo "Run the suggested pip commands above to fix this."
    exit 1
fi
echo ""

echo -e "${BLUE}=== Cleanup Complete ===${NC}"
echo ""
echo -e "${GREEN}Vector store has been cleaned and reset.${NC}"
echo ""
echo "Next steps:"
echo "  1. Start the API: bash start-api-noproxy.sh"
echo "  2. Monitor logs: tail -f logs/drass-api-*.log"
echo ""
echo "The vector store will be automatically initialized on first API start."