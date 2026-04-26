# Local Environment Test Plan for LangChain Compliance Assistant

## Test Overview
This comprehensive test plan covers all components of the LangChain Compliance Assistant in local environment, including frontend, backend, model services, and integration tests.

## Prerequisites

### Environment Setup
- [ ] macOS (tested on MacBook Pro)
- [ ] Node.js 18+ and npm installed
- [ ] Python 3.10+ installed
- [ ] Docker Desktop installed and running
- [ ] At least 16GB RAM available
- [ ] 20GB free disk space

### Service Requirements
- [ ] Ollama installed and running
- [ ] Local embedding service deployed
- [ ] PostgreSQL database running
- [ ] Redis cache running

## Test Execution Plan

### Phase 1: Infrastructure Setup Tests

#### TEST-INFRA-001: Local AI Stack Deployment
**Priority**: P0
**Duration**: 15 minutes
```bash
# Test Objective: Verify local AI stack can be deployed successfully

# Step 1: Deploy Ollama
./scripts/deploy_ollama.sh
# Expected: Ollama installed, models downloaded (qwen2.5:7b, nomic-embed-text)

# Step 2: Deploy Embedding Service
./scripts/deploy_local_embedding.sh
# Expected: Virtual environment created, dependencies installed, model downloaded

# Step 3: Test Ollama
python3 scripts/test_ollama.py
# Expected: All tests pass (connection, model availability, generation, embedding)

# Step 4: Test Embedding Service
cd services/embedding-service
./start_service.sh &
python3 test_embedding.py
# Expected: Service running on port 8001, all tests pass
```

#### TEST-INFRA-002: Database and Cache Setup
**Priority**: P0
**Duration**: 10 minutes
```bash
# Test Objective: Verify database and cache services are operational

# Step 1: Start PostgreSQL
docker run -d \
  --name postgres-test \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=compliance_db \
  -p 5432:5432 \
  postgres:15

# Step 2: Start Redis
docker run -d \
  --name redis-test \
  -p 6379:6379 \
  redis:7-alpine

# Step 3: Verify connections
psql -h localhost -U postgres -d compliance_db -c "SELECT version();"
redis-cli ping
# Expected: PostgreSQL version shown, Redis returns "PONG"
```

### Phase 2: Backend Service Tests

#### TEST-BACKEND-001: FastAPI Application Startup
**Priority**: P0
**Duration**: 5 minutes
```bash
# Test Objective: Verify backend API starts and responds correctly

cd services/main-app

# Step 1: Install dependencies
pip install -r requirements.txt

# Step 2: Set environment variables
export LLM_PROVIDER=ollama
export LLM_MODEL=qwen2.5:7b
export OLLAMA_BASE_URL=http://localhost:11434
export EMBEDDING_SERVICE_URL=http://localhost:8001
export DATABASE_URL=postgresql://postgres:password@localhost:5432/compliance_db
export REDIS_URL=redis://localhost:6379/0

# Step 3: Start application
uvicorn app.main:app --reload --port 8000

# Step 4: Test health endpoint
curl http://localhost:8000/health
# Expected: {"status": "healthy", "timestamp": "..."}

# Step 5: Test API documentation
open http://localhost:8000/docs
# Expected: Swagger UI loads with all endpoints
```

#### TEST-BACKEND-002: LangChain RAG Chain
**Priority**: P0
**Duration**: 10 minutes
```python
# test_rag_chain.py
import asyncio
import aiohttp
import json

async def test_rag_chain():
    """Test RAG chain functionality"""
    
    # Test 1: Simple query without context
    async with aiohttp.ClientSession() as session:
        payload = {
            "query": "什么是数据合规？",
            "stream": False
        }
        
        async with session.post(
            "http://localhost:8000/api/v1/chat/completions",
            json=payload
        ) as response:
            result = await response.json()
            assert response.status == 200
            assert "response" in result
            print(f"✓ RAG response: {result['response'][:100]}...")
    
    # Test 2: Query with document context
    # First upload a document
    with open("test_document.txt", "w") as f:
        f.write("公司数据合规政策：所有客户数据必须加密存储，访问需要审计日志。")
    
    async with aiohttp.ClientSession() as session:
        # Upload document
        with open("test_document.txt", "rb") as f:
            data = aiohttp.FormData()
            data.add_field('file', f, filename='test_document.txt')
            
            async with session.post(
                "http://localhost:8000/api/v1/documents/upload",
                data=data
            ) as response:
                assert response.status == 200
                print("✓ Document uploaded")
        
        # Query with context
        payload = {
            "query": "公司的数据存储政策是什么？",
            "use_knowledge_base": True,
            "stream": False
        }
        
        async with session.post(
            "http://localhost:8000/api/v1/chat/completions",
            json=payload
        ) as response:
            result = await response.json()
            assert "加密" in result['response']
            print(f"✓ RAG with context: {result['response'][:100]}...")

asyncio.run(test_rag_chain())
```

#### TEST-BACKEND-003: LangChain Agent System
**Priority**: P0
**Duration**: 10 minutes
```python
# test_agent_system.py
import asyncio
import aiohttp

async def test_agent_system():
    """Test agent system with tools"""
    
    async with aiohttp.ClientSession() as session:
        # Test compliance analysis agent
        payload = {
            "task": "analyze_compliance",
            "content": "我们公司收集用户的姓名、邮箱和手机号用于营销。",
            "regulations": ["GDPR", "个人信息保护法"]
        }
        
        async with session.post(
            "http://localhost:8000/api/v1/agent/execute",
            json=payload
        ) as response:
            result = await response.json()
            assert response.status == 200
            assert "analysis" in result
            assert "recommendations" in result
            print("✓ Agent analysis completed")
            print(f"  Risks found: {len(result.get('risks', []))}")
            print(f"  Recommendations: {len(result.get('recommendations', []))}")

asyncio.run(test_agent_system())
```

### Phase 3: Frontend Tests

#### TEST-FRONTEND-001: React Application Startup
**Priority**: P0
**Duration**: 5 minutes
```bash
# Test Objective: Verify frontend builds and runs

cd frontend

# Step 1: Install dependencies
npm install

# Step 2: Run type checking
npm run type-check
# Expected: Some warnings but no errors blocking compilation

# Step 3: Run unit tests
npm run test
# Expected: Test suites pass (may have some warnings)

# Step 4: Start development server
npm run dev
# Expected: Server starts on http://localhost:5173

# Step 5: Test in browser
open http://localhost:5173
# Expected: Application loads, ChatInterface visible
```

#### TEST-FRONTEND-002: Component Integration Tests
**Priority**: P0
**Duration**: 10 minutes
```typescript
// frontend/src/__tests__/integration.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { store } from '../store';
import ChatInterface from '../components/ChatInterface';

describe('ChatInterface Integration', () => {
  test('sends message and receives response', async () => {
    render(
      <Provider store={store}>
        <ChatInterface 
          apiEndpoint="http://localhost:8000/api/v1/chat"
          wsEndpoint="ws://localhost:8000/ws"
        />
      </Provider>
    );
    
    // Type message
    const input = screen.getByPlaceholderText('Type your message...');
    fireEvent.change(input, { target: { value: 'Hello assistant' } });
    
    // Send message
    const sendButton = screen.getByRole('button', { name: /send/i });
    fireEvent.click(sendButton);
    
    // Wait for response
    await waitFor(() => {
      expect(screen.getByText(/Hello assistant/)).toBeInTheDocument();
    }, { timeout: 5000 });
    
    // Check for assistant response
    await waitFor(() => {
      const messages = screen.getAllByTestId('message-item');
      expect(messages.length).toBeGreaterThan(1);
    }, { timeout: 10000 });
  });
});
```

#### TEST-FRONTEND-003: Document Upload Flow
**Priority**: P1
**Duration**: 10 minutes
```typescript
// frontend/src/__tests__/upload.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import DocumentUpload from '../components/DocumentUpload';

describe('Document Upload', () => {
  test('uploads file successfully', async () => {
    const onUploadComplete = jest.fn();
    
    render(
      <DocumentUpload 
        endpoint="http://localhost:8000/api/v1/documents/upload"
        onUploadComplete={onUploadComplete}
      />
    );
    
    // Create test file
    const file = new File(['test content'], 'test.txt', { type: 'text/plain' });
    const input = screen.getByLabelText(/drag.*drop/i);
    
    // Trigger file upload
    fireEvent.drop(input, {
      dataTransfer: { files: [file] }
    });
    
    // Wait for upload to complete
    await waitFor(() => {
      expect(screen.getByText(/uploaded successfully/i)).toBeInTheDocument();
    }, { timeout: 5000 });
    
    expect(onUploadComplete).toHaveBeenCalled();
  });
});
```

### Phase 4: Integration Tests

#### TEST-INTEGRATION-001: End-to-End Chat Flow
**Priority**: P0
**Duration**: 15 minutes
```bash
# Test Objective: Complete chat flow with RAG

# Step 1: Ensure all services are running
./start_local.sh

# Step 2: Run E2E test script
cat > test_e2e_chat.py << 'EOF'
import asyncio
import aiohttp
import json
from datetime import datetime

async def test_e2e_chat():
    """Test complete chat flow"""
    
    print("Starting E2E Chat Test...")
    session_id = f"test-session-{datetime.now().timestamp()}"
    
    async with aiohttp.ClientSession() as session:
        # 1. Create chat session
        async with session.post(
            "http://localhost:8000/api/v1/sessions",
            json={"title": "Test Session"}
        ) as response:
            session_data = await response.json()
            session_id = session_data["id"]
            print(f"✓ Session created: {session_id}")
        
        # 2. Upload document
        test_content = """
        数据保护条例：
        1. 所有个人数据必须加密存储
        2. 数据访问需要多因素认证
        3. 每月进行安全审计
        """
        
        with open("test_policy.txt", "w") as f:
            f.write(test_content)
        
        with open("test_policy.txt", "rb") as f:
            data = aiohttp.FormData()
            data.add_field('file', f, filename='test_policy.txt')
            data.add_field('session_id', session_id)
            
            async with session.post(
                "http://localhost:8000/api/v1/documents/upload",
                data=data
            ) as response:
                assert response.status == 200
                print("✓ Document uploaded to knowledge base")
        
        # 3. Send chat message with RAG
        async with session.post(
            "http://localhost:8000/api/v1/chat/completions",
            json={
                "session_id": session_id,
                "query": "我们的数据存储要求是什么？",
                "use_knowledge_base": True,
                "stream": False
            }
        ) as response:
            result = await response.json()
            assert "加密" in result["response"]
            print(f"✓ RAG response received: {result['response'][:100]}...")
        
        # 4. Test streaming response
        async with session.post(
            "http://localhost:8000/api/v1/chat/completions",
            json={
                "session_id": session_id,
                "query": "详细解释多因素认证",
                "stream": True
            }
        ) as response:
            chunks = []
            async for line in response.content:
                if line:
                    chunks.append(line.decode('utf-8'))
            
            assert len(chunks) > 0
            print(f"✓ Streaming response received: {len(chunks)} chunks")
        
        # 5. Get session history
        async with session.get(
            f"http://localhost:8000/api/v1/sessions/{session_id}/messages"
        ) as response:
            messages = await response.json()
            assert len(messages) >= 4  # System + 2 user + 2 assistant
            print(f"✓ Session history: {len(messages)} messages")
        
        print("\n✅ E2E Chat Test Completed Successfully!")

asyncio.run(test_e2e_chat())
EOF

python3 test_e2e_chat.py
```

#### TEST-INTEGRATION-002: WebSocket Real-time Communication
**Priority**: P0
**Duration**: 10 minutes
```javascript
// test_websocket.js
const WebSocket = require('ws');

async function testWebSocket() {
    console.log('Testing WebSocket connection...');
    
    const ws = new WebSocket('ws://localhost:8000/ws');
    
    return new Promise((resolve, reject) => {
        ws.on('open', () => {
            console.log('✓ WebSocket connected');
            
            // Send test message
            ws.send(JSON.stringify({
                type: 'chat',
                payload: {
                    query: 'Hello from WebSocket test',
                    session_id: 'test-ws-session'
                }
            }));
        });
        
        ws.on('message', (data) => {
            const message = JSON.parse(data);
            console.log('✓ Received:', message.type);
            
            if (message.type === 'chat') {
                console.log('✓ Chat response received');
                ws.close();
                resolve();
            }
        });
        
        ws.on('error', (error) => {
            console.error('✗ WebSocket error:', error);
            reject(error);
        });
        
        setTimeout(() => {
            ws.close();
            reject(new Error('WebSocket test timeout'));
        }, 10000);
    });
}

testWebSocket().catch(console.error);
```

### Phase 5: Performance Tests

#### TEST-PERF-001: Load Testing
**Priority**: P1
**Duration**: 10 minutes
```python
# test_performance.py
import asyncio
import aiohttp
import time
from concurrent.futures import ThreadPoolExecutor

async def single_request(session, query_num):
    """Send single chat request"""
    start = time.time()
    
    async with session.post(
        "http://localhost:8000/api/v1/chat/completions",
        json={
            "query": f"Test query {query_num}: What is data compliance?",
            "stream": False
        }
    ) as response:
        await response.json()
        return time.time() - start

async def load_test(concurrent_users=10, requests_per_user=5):
    """Run load test"""
    print(f"Load test: {concurrent_users} users, {requests_per_user} requests each")
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for user in range(concurrent_users):
            for req in range(requests_per_user):
                tasks.append(single_request(session, user * requests_per_user + req))
        
        start = time.time()
        response_times = await asyncio.gather(*tasks)
        total_time = time.time() - start
        
        # Calculate statistics
        avg_response = sum(response_times) / len(response_times)
        max_response = max(response_times)
        min_response = min(response_times)
        
        print(f"""
Performance Results:
- Total requests: {len(tasks)}
- Total time: {total_time:.2f}s
- Throughput: {len(tasks)/total_time:.2f} req/s
- Avg response time: {avg_response:.2f}s
- Max response time: {max_response:.2f}s
- Min response time: {min_response:.2f}s
        """)
        
        # Assert performance requirements
        assert avg_response < 5.0, "Average response time too high"
        assert max_response < 10.0, "Max response time too high"
        print("✅ Performance test passed!")

asyncio.run(load_test())
```

### Phase 6: Security Tests

#### TEST-SECURITY-001: Authentication and Authorization
**Priority**: P0
**Duration**: 5 minutes
```python
# test_security.py
import requests
import jwt

def test_authentication():
    """Test API authentication"""
    
    # Test 1: Access without token
    response = requests.get("http://localhost:8000/api/v1/protected")
    assert response.status_code == 401
    print("✓ Unauthorized access blocked")
    
    # Test 2: Login and get token
    response = requests.post(
        "http://localhost:8000/api/v1/auth/login",
        json={"username": "test_user", "password": "test_password"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    print("✓ Login successful")
    
    # Test 3: Access with valid token
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        "http://localhost:8000/api/v1/protected",
        headers=headers
    )
    assert response.status_code == 200
    print("✓ Authorized access granted")
    
    # Test 4: Invalid token
    headers = {"Authorization": "Bearer invalid_token"}
    response = requests.get(
        "http://localhost:8000/api/v1/protected",
        headers=headers
    )
    assert response.status_code == 401
    print("✓ Invalid token rejected")

test_authentication()
```

## Test Execution Script

Create a master test runner:

```bash
#!/bin/bash
# run_all_tests.sh

echo "=========================================="
echo "LangChain Compliance Assistant Test Suite"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

TESTS_PASSED=0
TESTS_FAILED=0

# Function to run test
run_test() {
    local test_name=$1
    local test_command=$2
    
    echo -e "\n${YELLOW}Running: $test_name${NC}"
    
    if eval "$test_command"; then
        echo -e "${GREEN}✓ $test_name passed${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ $test_name failed${NC}"
        ((TESTS_FAILED++))
    fi
}

# Phase 1: Infrastructure
run_test "Ollama Service" "curl -s http://localhost:11434/api/tags > /dev/null"
run_test "Embedding Service" "curl -s http://localhost:8001/health > /dev/null"
run_test "PostgreSQL" "pg_isready -h localhost -p 5432"
run_test "Redis" "redis-cli ping | grep -q PONG"

# Phase 2: Backend
run_test "Backend API" "curl -s http://localhost:8000/health | grep -q healthy"
run_test "RAG Chain" "python3 test_rag_chain.py"
run_test "Agent System" "python3 test_agent_system.py"

# Phase 3: Frontend
run_test "Frontend Build" "cd frontend && npm run build"
run_test "Frontend Tests" "cd frontend && npm test -- --run"

# Phase 4: Integration
run_test "E2E Chat Flow" "python3 test_e2e_chat.py"
run_test "WebSocket" "node test_websocket.js"

# Phase 5: Performance
run_test "Load Test" "python3 test_performance.py"

# Phase 6: Security
run_test "Authentication" "python3 test_security.py"

# Summary
echo -e "\n=========================================="
echo "Test Summary:"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✅ All tests passed! System ready for use.${NC}"
    exit 0
else
    echo -e "\n${RED}⚠️ Some tests failed. Please review the errors above.${NC}"
    exit 1
fi
```

## Test Data Preparation

Create test data files:

```bash
# create_test_data.sh
#!/bin/bash

echo "Creating test data..."

# Create test documents
cat > test_data/gdpr_compliance.md << 'EOF'
# GDPR Compliance Guidelines

## Data Protection Principles
1. Lawfulness, fairness and transparency
2. Purpose limitation
3. Data minimisation
4. Accuracy
5. Storage limitation
6. Integrity and confidentiality
7. Accountability

## User Rights
- Right to access
- Right to rectification
- Right to erasure
- Right to data portability
EOF

cat > test_data/china_pipl.md << 'EOF'
# 中国个人信息保护法要点

## 基本原则
1. 合法、正当、必要原则
2. 目的明确原则
3. 最小必要原则
4. 公开透明原则
5. 确保安全原则

## 个人权利
- 知情权
- 决定权
- 查阅权
- 更正权
- 删除权
EOF

echo "Test data created in test_data/"
```

## Continuous Testing

Add to package.json:

```json
{
  "scripts": {
    "test:local": "./run_all_tests.sh",
    "test:unit": "npm test -- --run",
    "test:integration": "npm run test:unit && python3 test_e2e_chat.py",
    "test:performance": "python3 test_performance.py",
    "test:security": "python3 test_security.py",
    "test:all": "npm run test:local"
  }
}
```

## Test Report Template

```markdown
# Test Execution Report

**Date**: [DATE]
**Environment**: Local Development
**Tester**: [NAME]

## Summary
- Total Tests: [NUMBER]
- Passed: [NUMBER]
- Failed: [NUMBER]
- Skipped: [NUMBER]

## Test Results

| Test ID | Test Name | Status | Duration | Notes |
|---------|-----------|--------|----------|-------|
| TEST-INFRA-001 | AI Stack Deployment | ✅ Pass | 15m | All models loaded |
| TEST-BACKEND-001 | API Startup | ✅ Pass | 5m | Health check OK |
| TEST-FRONTEND-001 | React App | ✅ Pass | 5m | Build successful |
| TEST-INTEGRATION-001 | E2E Chat | ✅ Pass | 15m | RAG working |

## Issues Found
1. [Issue description if any]

## Recommendations
1. [Recommendations if any]

## Sign-off
- Development: ✅
- QA: ⏳
- Product: ⏳
```

## Quick Test Commands

```bash
# Quick smoke test (5 minutes)
./test_local_stack.sh

# Full test suite (45 minutes)
./run_all_tests.sh

# Specific component tests
npm run test:unit        # Frontend unit tests
python3 test_rag_chain.py # Backend RAG tests
python3 test_e2e_chat.py  # Integration tests

# Performance baseline
python3 test_performance.py --baseline

# Security scan
python3 test_security.py --full
```

## Success Criteria

The system is considered ready for local development when:

1. ✅ All infrastructure services are running
2. ✅ Backend API responds to health checks
3. ✅ Frontend builds without errors
4. ✅ RAG chain returns relevant responses
5. ✅ Document upload and indexing works
6. ✅ WebSocket connections are stable
7. ✅ Average response time < 5 seconds
8. ✅ Can handle 10 concurrent users
9. ✅ Authentication is properly enforced
10. ✅ All unit tests pass with >70% coverage

## Troubleshooting Guide

Common issues and solutions:

| Issue | Solution |
|-------|----------|
| Ollama not responding | Run `ollama serve` and check port 11434 |
| Embedding service timeout | Increase timeout in config, check model download |
| Database connection refused | Check PostgreSQL is running on port 5432 |
| Frontend build errors | Clear node_modules and reinstall |
| WebSocket connection failed | Check CORS settings in backend |
| Slow RAG responses | Check vector store indexing, reduce chunk size |
| Memory issues | Increase Docker memory limit to 8GB |

---

This comprehensive test plan ensures all components work correctly in the local environment before deployment.