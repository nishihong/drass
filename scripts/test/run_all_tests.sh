#!/bin/bash

# Comprehensive Test Runner for LangChain Compliance Assistant
# This script runs all tests in sequence and provides a summary report

echo "=========================================="
echo "LangChain Compliance Assistant Test Suite"
echo "=========================================="
echo "Environment: Local Development"
echo "Date: $(date)"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

# Test results array
declare -a TEST_RESULTS

# Project root
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Function to check if service is running
check_service() {
    local service_name=$1
    local check_command=$2
    
    echo -ne "Checking $service_name... "
    
    if eval "$check_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
        return 0
    else
        echo -e "${RED}✗${NC}"
        return 1
    fi
}

# Function to run test
run_test() {
    local test_id=$1
    local test_name=$2
    local test_command=$3
    local test_type=${4:-"AUTO"}
    
    echo -e "\n${YELLOW}[$test_id] Running: $test_name${NC}"
    echo "Type: $test_type"
    
    START_TIME=$(date +%s)
    
    if [ "$test_type" = "MANUAL" ]; then
        echo "⚠️  This test requires manual verification"
        echo "Command: $test_command"
        TEST_RESULTS+=("$test_id|$test_name|SKIPPED|0s|Manual test")
        ((TESTS_SKIPPED++))
    else
        if eval "$test_command" > /tmp/test_output_$test_id.log 2>&1; then
            END_TIME=$(date +%s)
            DURATION=$((END_TIME - START_TIME))
            echo -e "${GREEN}✓ PASSED${NC} (${DURATION}s)"
            TEST_RESULTS+=("$test_id|$test_name|PASSED|${DURATION}s|Success")
            ((TESTS_PASSED++))
        else
            END_TIME=$(date +%s)
            DURATION=$((END_TIME - START_TIME))
            echo -e "${RED}✗ FAILED${NC} (${DURATION}s)"
            echo "Error output:"
            tail -n 5 /tmp/test_output_$test_id.log
            TEST_RESULTS+=("$test_id|$test_name|FAILED|${DURATION}s|See /tmp/test_output_$test_id.log")
            ((TESTS_FAILED++))
        fi
    fi
}

# Create test data directory
mkdir -p test_data
mkdir -p test_reports

echo -e "\n${BLUE}=== Phase 0: Prerequisites Check ===${NC}"

# Check prerequisites
PREREQ_OK=true

check_service "Node.js" "node --version" || PREREQ_OK=false
check_service "Python" "python3 --version" || PREREQ_OK=false
check_service "Docker" "docker --version" || PREREQ_OK=false
check_service "Git" "git --version" || PREREQ_OK=false

if [ "$PREREQ_OK" = false ]; then
    echo -e "\n${RED}Prerequisites not met. Please install missing components.${NC}"
    exit 1
fi

echo -e "\n${BLUE}=== Phase 1: Infrastructure Tests ===${NC}"

# Check if services are running
run_test "INFRA-001" "Ollama Service Check" \
    "curl -s http://localhost:11434/api/tags"

run_test "INFRA-002" "Embedding Service Check" \
    "curl -s http://localhost:8001/health | grep -q healthy"

run_test "INFRA-003" "PostgreSQL Check" \
    "pg_isready -h localhost -p 5432 -U postgres"

run_test "INFRA-004" "Redis Check" \
    "redis-cli ping | grep -q PONG"

echo -e "\n${BLUE}=== Phase 2: Backend Tests ===${NC}"

# Create Python test script for RAG
cat > /tmp/test_rag.py << 'EOF'
import sys
import requests
import json

try:
    # Test health endpoint
    response = requests.get("http://localhost:8000/health", timeout=5)
    assert response.status_code == 200, f"Health check failed: {response.status_code}"
    
    # Test chat endpoint
    payload = {
        "query": "What is data compliance?",
        "stream": False
    }
    response = requests.post(
        "http://localhost:8000/api/v1/chat/completions",
        json=payload,
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        assert "response" in result or "choices" in result, "Invalid response format"
        print("RAG test passed")
        sys.exit(0)
    else:
        print(f"Chat endpoint failed: {response.status_code}")
        sys.exit(1)
        
except Exception as e:
    print(f"Test failed: {e}")
    sys.exit(1)
EOF

run_test "BACKEND-001" "FastAPI Health Check" \
    "curl -s http://localhost:8000/health | grep -q healthy"

run_test "BACKEND-002" "RAG Chain Test" \
    "python3 /tmp/test_rag.py"

echo -e "\n${BLUE}=== Phase 3: Frontend Tests ===${NC}"

# Frontend tests
cd "$PROJECT_ROOT/frontend" || exit 1

run_test "FRONTEND-001" "NPM Dependencies" \
    "npm list --depth=0"

run_test "FRONTEND-002" "TypeScript Compilation" \
    "npm run type-check"

run_test "FRONTEND-003" "Frontend Unit Tests" \
    "npm test -- --run"

run_test "FRONTEND-004" "Frontend Build" \
    "npm run build"

cd "$PROJECT_ROOT" || exit 1

echo -e "\n${BLUE}=== Phase 4: Integration Tests ===${NC}"

# Create WebSocket test
cat > /tmp/test_websocket.js << 'EOF'
const WebSocket = require('ws');

const ws = new WebSocket('ws://localhost:8000/ws');
let timeout;

ws.on('open', () => {
    console.log('WebSocket connected');
    ws.send(JSON.stringify({
        type: 'ping',
        payload: null
    }));
    
    timeout = setTimeout(() => {
        console.error('No response received');
        process.exit(1);
    }, 5000);
});

ws.on('message', (data) => {
    clearTimeout(timeout);
    console.log('Response received');
    ws.close();
    process.exit(0);
});

ws.on('error', (error) => {
    console.error('WebSocket error:', error.message);
    process.exit(1);
});
EOF

run_test "INTEGRATION-001" "WebSocket Connection" \
    "node /tmp/test_websocket.js"

# Create E2E test
cat > /tmp/test_e2e.py << 'EOF'
import sys
import requests
import time

try:
    # Test complete flow
    print("Testing E2E flow...")
    
    # 1. Check services
    services = [
        ("Frontend", "http://localhost:5173"),
        ("Backend", "http://localhost:8000/health"),
        ("Ollama", "http://localhost:11434/api/tags"),
        ("Embedding", "http://localhost:8001/health")
    ]
    
    for name, url in services:
        try:
            response = requests.get(url, timeout=5)
            print(f"✓ {name} is running")
        except:
            print(f"✗ {name} is not accessible")
            sys.exit(1)
    
    # 2. Test chat flow
    response = requests.post(
        "http://localhost:8000/api/v1/chat/completions",
        json={"query": "Hello", "stream": False},
        timeout=30
    )
    
    if response.status_code == 200:
        print("✓ Chat API working")
    else:
        print(f"✗ Chat API failed: {response.status_code}")
        sys.exit(1)
    
    print("E2E test passed")
    sys.exit(0)
    
except Exception as e:
    print(f"E2E test failed: {e}")
    sys.exit(1)
EOF

run_test "INTEGRATION-002" "End-to-End Flow" \
    "python3 /tmp/test_e2e.py"

echo -e "\n${BLUE}=== Phase 5: Performance Tests ===${NC}"

# Simple performance test
cat > /tmp/test_performance.py << 'EOF'
import sys
import time
import requests
import statistics

response_times = []

print("Running performance test (10 requests)...")

for i in range(10):
    start = time.time()
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/chat/completions",
            json={"query": f"Test query {i}", "stream": False},
            timeout=30
        )
        duration = time.time() - start
        response_times.append(duration)
        print(f"Request {i+1}: {duration:.2f}s")
    except Exception as e:
        print(f"Request {i+1} failed: {e}")
        sys.exit(1)

avg_time = statistics.mean(response_times)
max_time = max(response_times)
min_time = min(response_times)

print(f"\nResults:")
print(f"Average: {avg_time:.2f}s")
print(f"Max: {max_time:.2f}s")
print(f"Min: {min_time:.2f}s")

if avg_time < 10:
    print("Performance test passed")
    sys.exit(0)
else:
    print("Performance test failed: Average response time too high")
    sys.exit(1)
EOF

run_test "PERF-001" "Response Time Test" \
    "python3 /tmp/test_performance.py"

echo -e "\n${BLUE}=== Phase 6: Manual Tests (Skipped in Automation) ===${NC}"

run_test "MANUAL-001" "UI Visual Inspection" \
    "Open http://localhost:5173 and verify UI loads correctly" \
    "MANUAL"

run_test "MANUAL-002" "Document Upload UI" \
    "Test document upload through UI" \
    "MANUAL"

# Generate test report
echo -e "\n${BLUE}=== Generating Test Report ===${NC}"

REPORT_FILE="test_reports/test_report_$(date +%Y%m%d_%H%M%S).md"

cat > "$REPORT_FILE" << EOF
# Test Execution Report

**Date**: $(date)
**Environment**: Local Development
**Test Suite Version**: 1.0.0

## Summary
- **Total Tests**: $((TESTS_PASSED + TESTS_FAILED + TESTS_SKIPPED))
- **Passed**: $TESTS_PASSED ✅
- **Failed**: $TESTS_FAILED ❌
- **Skipped**: $TESTS_SKIPPED ⏭️
- **Pass Rate**: $(echo "scale=2; $TESTS_PASSED * 100 / ($TESTS_PASSED + $TESTS_FAILED)" | bc)%

## Test Results

| Test ID | Test Name | Status | Duration | Notes |
|---------|-----------|--------|----------|-------|
EOF

for result in "${TEST_RESULTS[@]}"; do
    IFS='|' read -r id name status duration notes <<< "$result"
    echo "| $id | $name | $status | $duration | $notes |" >> "$REPORT_FILE"
done

cat >> "$REPORT_FILE" << EOF

## System Information
- **OS**: $(uname -s) $(uname -r)
- **Node.js**: $(node --version)
- **Python**: $(python3 --version)
- **Docker**: $(docker --version)

## Recommendations
EOF

if [ $TESTS_FAILED -gt 0 ]; then
    cat >> "$REPORT_FILE" << EOF
1. Review failed test logs in /tmp/test_output_*.log
2. Ensure all services are properly configured
3. Check network connectivity between services
4. Verify environment variables are set correctly
EOF
else
    cat >> "$REPORT_FILE" << EOF
1. System is ready for development use
2. Consider running performance tests with higher load
3. Execute manual UI tests for complete validation
EOF
fi

echo -e "\nTest report saved to: $REPORT_FILE"

# Final Summary
echo -e "\n${BLUE}=========================================="
echo "Test Execution Summary"
echo "==========================================${NC}"
echo -e "Passed:  ${GREEN}$TESTS_PASSED${NC}"
echo -e "Failed:  ${RED}$TESTS_FAILED${NC}"
echo -e "Skipped: ${YELLOW}$TESTS_SKIPPED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✅ All automated tests passed!${NC}"
    echo "The system is ready for local development."
    echo ""
    echo "Next steps:"
    echo "1. Review the test report at: $REPORT_FILE"
    echo "2. Execute manual UI tests"
    echo "3. Start development with: ./start_local.sh"
    exit 0
else
    echo -e "\n${RED}⚠️  Some tests failed!${NC}"
    echo "Please review the errors and fix issues before proceeding."
    echo ""
    echo "Debug information:"
    echo "- Test logs: /tmp/test_output_*.log"
    echo "- Test report: $REPORT_FILE"
    echo ""
    echo "Common fixes:"
    echo "1. Start all services: ./start_local.sh"
    echo "2. Check service logs: docker-compose logs"
    echo "3. Verify environment: cat .env.local"
    exit 1
fi