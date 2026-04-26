#!/bin/bash

# Fix missing dependencies for Drass backend
# This script installs all required Python packages that might be missing

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Detect the actual directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="$SCRIPT_DIR"
VENV_DIR="$BASE_DIR/venv"

echo -e "${BLUE}=== Fixing Drass Backend Dependencies ===${NC}"
echo "Date: $(date)"
echo ""

# 1. Check if virtual environment exists
if [ -d "$VENV_DIR" ]; then
    echo -e "${BLUE}Activating virtual environment...${NC}"
    source "$VENV_DIR/bin/activate"
    echo "Python: $(which python)"
    echo "Pip: $(which pip)"
else
    echo -e "${YELLOW}No virtual environment found, using system Python${NC}"
fi

echo ""

# 2. Upgrade pip
echo -e "${BLUE}Step 1: Upgrading pip...${NC}"
pip install --upgrade pip
echo -e "${GREEN}✓${NC} Pip upgraded"
echo ""

# 3. Install core document processing libraries
echo -e "${BLUE}Step 2: Installing document processing libraries...${NC}"

# PDF processing
echo "Installing PDF processing libraries..."
pip install PyPDF2 pypdf pdfplumber pymupdf4llm 2>/dev/null || {
    echo -e "${YELLOW}Some PDF libraries failed, trying alternatives...${NC}"
    pip install pypdf2 2>/dev/null || pip install pypdf 2>/dev/null
}

# Document processing
echo "Installing document processing libraries..."
pip install python-docx openpyxl python-pptx 2>/dev/null || {
    echo -e "${YELLOW}Some document libraries failed${NC}"
}

# OCR support (optional)
echo "Installing OCR libraries (optional)..."
pip install pytesseract pdf2image 2>/dev/null || {
    echo -e "${YELLOW}OCR libraries not installed (optional)${NC}"
}

# Markdown conversion
echo "Installing markdown libraries..."
pip install markdownify beautifulsoup4 html2text 2>/dev/null

echo -e "${GREEN}✓${NC} Document processing libraries installed"
echo ""

# 4. Install/upgrade LangChain and related packages
echo -e "${BLUE}Step 3: Installing/upgrading LangChain packages...${NC}"

# Core LangChain packages
echo "Installing LangChain core packages..."
pip install --upgrade langchain langchain-community langchain-core langchain-openai 2>/dev/null

# LangChain extras
echo "Installing LangChain extras..."
pip install --upgrade langchain-text-splitters langchain-chroma 2>/dev/null || true

echo -e "${GREEN}✓${NC} LangChain packages installed"
echo ""

# 5. Install vector store dependencies
echo -e "${BLUE}Step 4: Installing vector store dependencies...${NC}"

# ChromaDB
echo "Installing ChromaDB..."
pip install --upgrade chromadb 2>/dev/null || {
    echo -e "${YELLOW}ChromaDB installation failed, trying with specific version...${NC}"
    pip install chromadb==0.4.24 2>/dev/null || true
}

# Embeddings
echo "Installing embedding libraries..."
pip install --upgrade sentence-transformers transformers 2>/dev/null

echo -e "${GREEN}✓${NC} Vector store dependencies installed"
echo ""

# 6. Install API and authentication dependencies
echo -e "${BLUE}Step 5: Installing API dependencies...${NC}"

echo "Installing FastAPI and related packages..."
pip install --upgrade fastapi uvicorn[standard] python-multipart 2>/dev/null

echo "Installing authentication packages..."
pip install --upgrade passlib[bcrypt] bcrypt python-jose[cryptography] 2>/dev/null

echo "Installing HTTP clients..."
pip install --upgrade httpx aiohttp aiofiles 2>/dev/null

echo -e "${GREEN}✓${NC} API dependencies installed"
echo ""

# 7. Install database dependencies
echo -e "${BLUE}Step 6: Installing database dependencies...${NC}"

echo "Installing database drivers..."
pip install --upgrade sqlalchemy psycopg2-binary asyncpg redis 2>/dev/null

echo -e "${GREEN}✓${NC} Database dependencies installed"
echo ""

# 8. Install utility packages
echo -e "${BLUE}Step 7: Installing utility packages...${NC}"

echo "Installing utility libraries..."
pip install --upgrade python-dotenv pydantic pydantic-settings 2>/dev/null
pip install --upgrade tenacity retry backoff 2>/dev/null
pip install --upgrade tqdm rich click 2>/dev/null

echo -e "${GREEN}✓${NC} Utility packages installed"
echo ""

# 9. Check specific problematic packages
echo -e "${BLUE}Step 8: Checking critical packages...${NC}"

# Check PyPDF2
python -c "import PyPDF2; print('✓ PyPDF2 version:', PyPDF2.__version__)" 2>/dev/null || {
    python -c "import pypdf; print('✓ pypdf installed as alternative')" 2>/dev/null || {
        echo -e "${RED}✗ PDF processing library not available${NC}"
        echo "Trying manual installation..."
        pip install --force-reinstall pypdf 2>/dev/null
    }
}

# Check bcrypt
python -c "import bcrypt; print('✓ bcrypt version:', bcrypt.__version__)" 2>/dev/null || {
    echo -e "${YELLOW}bcrypt not properly installed, reinstalling...${NC}"
    pip uninstall -y bcrypt 2>/dev/null
    pip install bcrypt 2>/dev/null
}

# Check httpx
python -c "import httpx; print('✓ httpx version:', httpx.__version__)" 2>/dev/null || {
    echo -e "${RED}✗ httpx not available${NC}"
}

# Check langchain
python -c "import langchain; print('✓ langchain version:', langchain.__version__)" 2>/dev/null || {
    echo -e "${RED}✗ langchain not available${NC}"
}

echo ""

# 10. Create requirements file if missing
echo -e "${BLUE}Step 9: Creating updated requirements file...${NC}"

cat > "$BASE_DIR/services/main-app/requirements-fixed.txt" << 'EOF'
# Core FastAPI
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
python-multipart>=0.0.6

# Authentication
passlib[bcrypt]>=1.7.4
bcrypt>=4.0.0
python-jose[cryptography]>=3.3.0

# Database
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
asyncpg>=0.28.0
redis>=4.5.0

# HTTP clients
httpx>=0.24.0
aiohttp>=3.8.0
aiofiles>=23.0.0

# LangChain
langchain>=0.1.0
langchain-community>=0.0.10
langchain-core>=0.1.0
langchain-openai>=0.0.5
langchain-text-splitters>=0.0.1

# Document processing
PyPDF2>=3.0.0
pypdf>=3.0.0
python-docx>=0.8.11
openpyxl>=3.1.0
python-pptx>=0.6.21
markdownify>=0.11.0
beautifulsoup4>=4.12.0
html2text>=2020.1.16

# Vector stores
chromadb>=0.4.0
sentence-transformers>=2.2.0

# OpenAI compatible
openai>=1.0.0

# Utilities
python-dotenv>=1.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
tenacity>=8.2.0
tqdm>=4.65.0

# Optional OCR
# pytesseract
# pdf2image
EOF

echo -e "${GREEN}✓${NC} Requirements file created at: $BASE_DIR/services/main-app/requirements-fixed.txt"
echo ""

# 11. Test imports
echo -e "${BLUE}Step 10: Testing critical imports...${NC}"

python << EOF
import sys
print("Python version:", sys.version)
print("")

critical_modules = [
    ("PyPDF2 or pypdf", ["PyPDF2", "pypdf"]),
    ("FastAPI", ["fastapi"]),
    ("LangChain", ["langchain"]),
    ("ChromaDB", ["chromadb"]),
    ("HTTPx", ["httpx"]),
    ("Passlib", ["passlib"]),
    ("Jose", ["jose"]),
]

failed = []
for name, modules in critical_modules:
    imported = False
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {name} ({module})")
            imported = True
            break
        except ImportError:
            continue
    if not imported:
        print(f"✗ {name} - MISSING")
        failed.append(name)

if failed:
    print(f"\n⚠ Missing modules: {', '.join(failed)}")
    print("You may need to install them manually")
else:
    print("\n✓ All critical modules are available")
EOF

echo ""
echo -e "${BLUE}=== Dependency Fix Complete ===${NC}"
echo ""
echo "Next steps:"
echo "1. Restart the API: bash start-api-noproxy.sh"
echo "2. Check the API health: curl http://localhost:8888/health"
echo ""
echo "If you still have issues, check:"
echo "  tail -f logs/drass-api-*.log"