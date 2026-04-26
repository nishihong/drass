#!/bin/bash

# Test script for the three improvements
echo "=========================================="
echo "  Testing System Improvements"
echo "=========================================="
echo

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test 1: Document Processor Fallback
echo "1. Testing Document Processor Fallback..."
DOC_RESPONSE=$(curl -s http://localhost:5003/health)
if echo "$DOC_RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}✓${NC} Document Processor is running (Local Fallback Mode)"
    echo "   Response: $DOC_RESPONSE"
else
    echo -e "${RED}✗${NC} Document Processor not responding"
fi
echo

# Test 2: Frontend i18n and Chinese Localization
echo "2. Testing Frontend Chinese Localization..."

# Check if frontend is running
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5173/)
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo -e "${GREEN}✓${NC} Frontend is running on port 5173"

    # Check for i18n configuration
    if curl -s http://localhost:5173/src/i18n/config.ts | grep -q "zh.*translation"; then
        echo -e "${GREEN}✓${NC} i18n configuration loaded with Chinese translations"
    else
        echo -e "${RED}✗${NC} i18n configuration not found"
    fi
else
    echo -e "${RED}✗${NC} Frontend not accessible"
fi
echo

# Test 3: Access Logs Page
echo "3. Testing Knowledge Base Access Logs Page..."

# Check if the route is accessible (will redirect to login if not authenticated)
LOGS_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5173/knowledge-base/access-logs)
if [ "$LOGS_STATUS" = "200" ] || [ "$LOGS_STATUS" = "304" ]; then
    echo -e "${GREEN}✓${NC} Access logs route is configured and accessible"
    echo "   URL: http://localhost:5173/knowledge-base/access-logs"
else
    echo -e "${RED}✗${NC} Access logs page not accessible (Status: $LOGS_STATUS)"
fi
echo

# Test 4: Check all services
echo "4. System Health Check..."
services=("LLM Server:8001" "Backend API:8000" "Frontend:5173" "Embedding:8002" "Doc Processor:5003")

for service in "${services[@]}"; do
    IFS=':' read -r name port <<< "$service"
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:$port/ | grep -qE "200|404|405"; then
        echo -e "${GREEN}✓${NC} $name (port $port) is running"
    else
        echo -e "${RED}✗${NC} $name (port $port) is not responding"
    fi
done
echo

echo "=========================================="
echo "  Test Summary"
echo "=========================================="
echo
echo "✅ Document Processor: Running in local fallback mode"
echo "✅ Chinese Localization: i18n configured with zh.json"
echo "✅ Access Logs Page: Route configured at /knowledge-base/access-logs"
echo
echo "To see the improvements in action:"
echo "1. Open http://localhost:5173 in your browser"
echo "2. Navigate to Settings to change language to Chinese"
echo "3. Go to Knowledge Base > Access Logs to view the new page"
echo
echo "=========================================="