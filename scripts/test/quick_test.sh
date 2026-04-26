#!/bin/bash

# Quick Smoke Test for LangChain Compliance Assistant
# This script performs basic checks to ensure the system is ready

echo "======================================"
echo "Quick Smoke Test"
echo "======================================"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

CHECKS_PASSED=0
CHECKS_FAILED=0

# Function to check service
check() {
    local name=$1
    local command=$2
    
    echo -ne "Checking $name... "
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
        ((CHECKS_PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC}"
        ((CHECKS_FAILED++))
        return 1
    fi
}

echo -e "\n1. Environment Checks:"
check "Node.js" "node --version"
check "Python" "python3 --version"
check "npm" "npm --version"
check "pip" "pip3 --version"

echo -e "\n2. Service Availability:"
check "Ollama API" "curl -s http://localhost:11434/api/tags"
check "Embedding Service" "curl -s http://localhost:8001/health"
check "Backend API" "curl -s http://localhost:8000/health"
check "Frontend Dev Server" "curl -s http://localhost:5173"

echo -e "\n3. Database Connections:"
check "PostgreSQL" "pg_isready -h localhost -p 5432 2>/dev/null || echo 'SELECT 1' | psql -h localhost -U postgres -d compliance_db 2>/dev/null"
check "Redis" "redis-cli ping 2>/dev/null | grep -q PONG"

echo -e "\n4. Quick Functionality Test:"

# Test Ollama
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -ne "Testing Ollama generation... "
    RESPONSE=$(curl -s -X POST http://localhost:11434/api/generate \
        -d '{"model":"qwen2.5:7b","prompt":"Say hello","stream":false}' 2>/dev/null)
    
    if [ $? -eq 0 ] && [ -n "$RESPONSE" ]; then
        echo -e "${GREEN}✓${NC}"
        ((CHECKS_PASSED++))
    else
        echo -e "${YELLOW}⚠ Ollama running but model may not be loaded${NC}"
    fi
fi

# Test Backend Chat API
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -ne "Testing Chat API... "
    RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/chat/completions \
        -H "Content-Type: application/json" \
        -d '{"query":"Hello","stream":false}' 2>/dev/null)
    
    if [ $? -eq 0 ] && echo "$RESPONSE" | grep -q "response\|choices\|error"; then
        echo -e "${GREEN}✓${NC}"
        ((CHECKS_PASSED++))
    else
        echo -e "${YELLOW}⚠ API running but may need configuration${NC}"
    fi
fi

echo -e "\n======================================"
echo "Results:"
echo -e "Passed: ${GREEN}$CHECKS_PASSED${NC}"
echo -e "Failed: ${RED}$CHECKS_FAILED${NC}"

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✅ System is ready!${NC}"
    echo ""
    echo "You can now:"
    echo "1. Access the frontend at http://localhost:5173"
    echo "2. View API docs at http://localhost:8000/docs"
    echo "3. Run full test suite with: ./run_all_tests.sh"
else
    echo -e "\n${YELLOW}⚠️ Some services are not running${NC}"
    echo ""
    echo "To start all services, run:"
    echo "  ./start_local.sh"
    echo ""
    echo "To deploy local AI stack, run:"
    echo "  ./scripts/deploy_local_all.sh"
fi

exit $CHECKS_FAILED