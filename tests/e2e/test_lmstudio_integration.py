#!/usr/bin/env python3
"""
LM Studio Integration Test for Drass Compliance Assistant
Tests the complete integration with LM Studio serving Qwen2.5-8B model
"""

import os
import sys
import time
import requests
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add project to path
sys.path.insert(0, str(Path(__file__).parent / "services" / "main-app"))

# Load environment variables
load_dotenv(".env.local")

# Color codes for output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

def print_colored(message: str, color: str = NC):
    """Print colored message"""
    print(f"{color}{message}{NC}")

def test_lmstudio_server():
    """Test if LM Studio server is running"""
    print_colored("\n1. Testing LM Studio Server Status...", BLUE)
    
    base_url = os.getenv("LLM_BASE_URL", "http://localhost:1234/v1")
    
    try:
        # Test models endpoint
        response = requests.get(f"{base_url}/models", timeout=5)
        
        if response.status_code == 200:
            models = response.json()
            print_colored("✓ LM Studio server is running", GREEN)
            print(f"   Available models: {models.get('data', [])}")
            return True
        else:
            print_colored(f"✗ Server returned status {response.status_code}", RED)
            return False
            
    except requests.exceptions.ConnectionError:
        print_colored("✗ Cannot connect to LM Studio server", RED)
        print_colored("   Please start LM Studio and the local server:", YELLOW)
        print("   1. Open LM Studio application")
        print("   2. Go to 'Local Server' tab")
        print("   3. Select Qwen2.5-8B model")
        print("   4. Click 'Start Server'")
        return False
    except Exception as e:
        print_colored(f"✗ Error: {e}", RED)
        return False

def test_openai_compatibility():
    """Test OpenAI API compatibility"""
    print_colored("\n2. Testing OpenAI API Compatibility...", BLUE)
    
    base_url = os.getenv("LLM_BASE_URL", "http://localhost:1234/v1")
    
    try:
        payload = {
            "model": os.getenv("LLM_MODEL", "qwen2.5-8b"),
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'API test successful!' in exactly those words."}
            ],
            "temperature": 0.7,
            "max_tokens": 20,
            "stream": False
        }
        
        response = requests.post(
            f"{base_url}/chat/completions",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print_colored("✓ OpenAI API compatibility confirmed", GREEN)
            print(f"   Model response: {content}")
            return True
        else:
            print_colored(f"✗ API returned status {response.status_code}", RED)
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print_colored(f"✗ Error testing API: {e}", RED)
        return False

def test_streaming():
    """Test streaming capability"""
    print_colored("\n3. Testing Streaming Response...", BLUE)
    
    base_url = os.getenv("LLM_BASE_URL", "http://localhost:1234/v1")
    
    try:
        payload = {
            "model": os.getenv("LLM_MODEL", "qwen2.5-8b"),
            "messages": [
                {"role": "user", "content": "Count from 1 to 5 slowly."}
            ],
            "temperature": 0.7,
            "max_tokens": 50,
            "stream": True
        }
        
        response = requests.post(
            f"{base_url}/chat/completions",
            json=payload,
            headers={"Content-Type": "application/json"},
            stream=True,
            timeout=30
        )
        
        if response.status_code == 200:
            print_colored("✓ Streaming response received", GREEN)
            print("   Stream content: ", end="")
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith("data: "):
                        data = line_str[6:]
                        if data != "[DONE]":
                            print(".", end="", flush=True)
            print()
            return True
        else:
            print_colored(f"✗ Streaming failed with status {response.status_code}", RED)
            return False
            
    except Exception as e:
        print_colored(f"✗ Error testing streaming: {e}", RED)
        return False

def test_langchain_integration():
    """Test LangChain integration with LM Studio"""
    print_colored("\n4. Testing LangChain Integration...", BLUE)
    
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage, SystemMessage
        
        # Create LangChain LLM instance
        llm = ChatOpenAI(
            model=os.getenv("LLM_MODEL", "qwen2.5-8b"),
            openai_api_key="not-required",  # LM Studio doesn't need key
            openai_api_base=os.getenv("LLM_BASE_URL", "http://localhost:1234/v1"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "100")),
            streaming=True
        )
        
        # Test basic invocation
        messages = [
            SystemMessage(content="You are a compliance assistant."),
            HumanMessage(content="What is GDPR in one sentence?")
        ]
        
        response = llm.invoke(messages)
        
        if response and response.content:
            print_colored("✓ LangChain integration successful", GREEN)
            print(f"   Response: {response.content[:100]}...")
            return True
        else:
            print_colored("✗ No response from LangChain", RED)
            return False
            
    except ImportError:
        print_colored("⚠ LangChain not installed, skipping integration test", YELLOW)
        return None
    except Exception as e:
        print_colored(f"✗ LangChain integration error: {e}", RED)
        return False

async def test_rag_chain():
    """Test RAG chain with LM Studio"""
    print_colored("\n5. Testing RAG Chain with LM Studio...", BLUE)
    
    try:
        from app.chains.compliance_rag_chain import ComplianceRAGChain
        from langchain_community.vectorstores import Chroma
        from langchain_openai import OpenAIEmbeddings
        
        # Create embeddings (using local or OpenAI)
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=os.getenv("EMBEDDING_API_KEY", "test-key")
        )
        
        # Create in-memory vector store for testing
        texts = [
            "GDPR is the General Data Protection Regulation.",
            "GDPR applies to all EU citizens' data.",
            "Data breaches must be reported within 72 hours under GDPR."
        ]
        
        vector_store = Chroma.from_texts(
            texts=texts,
            embedding=embeddings,
            collection_name="test_collection"
        )
        
        # Create RAG chain
        rag_chain = ComplianceRAGChain(
            vector_store=vector_store,
            k=3
        )
        
        # Test query
        query = "What is GDPR?"
        response = await rag_chain.aquery(query)
        
        if response and "answer" in response:
            print_colored("✓ RAG chain with LM Studio works", GREEN)
            print(f"   Answer: {response['answer'][:100]}...")
            return True
        else:
            print_colored("✗ RAG chain returned no answer", RED)
            return False
            
    except ImportError as e:
        print_colored(f"⚠ Required modules not installed: {e}", YELLOW)
        return None
    except Exception as e:
        print_colored(f"✗ RAG chain error: {e}", RED)
        return False

def test_compliance_agent():
    """Test compliance agent with LM Studio"""
    print_colored("\n6. Testing Compliance Agent...", BLUE)
    
    try:
        from app.agents.compliance_agent import ComplianceAgent
        
        # Create agent
        agent = ComplianceAgent()
        
        # Test simple query
        result = agent.process(
            "What are the key requirements for GDPR compliance?",
            context={"user_id": "test_user"}
        )
        
        if result and "output" in result:
            print_colored("✓ Compliance agent works with LM Studio", GREEN)
            print(f"   Output: {str(result['output'])[:100]}...")
            return True
        else:
            print_colored("✗ Agent returned no output", RED)
            return False
            
    except ImportError as e:
        print_colored(f"⚠ Agent modules not installed: {e}", YELLOW)
        return None
    except Exception as e:
        print_colored(f"✗ Agent error: {e}", RED)
        return False

def test_performance():
    """Test performance metrics"""
    print_colored("\n7. Testing Performance Metrics...", BLUE)
    
    base_url = os.getenv("LLM_BASE_URL", "http://localhost:1234/v1")
    
    try:
        # Measure response time
        start_time = time.time()
        
        payload = {
            "model": os.getenv("LLM_MODEL", "qwen2.5-8b"),
            "messages": [
                {"role": "user", "content": "What is 2+2?"}
            ],
            "temperature": 0.1,
            "max_tokens": 10
        }
        
        response = requests.post(
            f"{base_url}/chat/completions",
            json=payload,
            timeout=30
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract token usage if available
            usage = result.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            
            print_colored("✓ Performance metrics collected", GREEN)
            print(f"   Response time: {response_time:.2f} seconds")
            print(f"   Prompt tokens: {prompt_tokens}")
            print(f"   Completion tokens: {completion_tokens}")
            
            if response_time < 2:
                print_colored("   ✓ Good response time (<2s)", GREEN)
            elif response_time < 5:
                print_colored("   ⚠ Moderate response time (2-5s)", YELLOW)
            else:
                print_colored("   ✗ Slow response time (>5s)", RED)
            
            return True
        else:
            print_colored(f"✗ Performance test failed: {response.status_code}", RED)
            return False
            
    except Exception as e:
        print_colored(f"✗ Error testing performance: {e}", RED)
        return False

def main():
    """Run all integration tests"""
    print_colored("=" * 60, BLUE)
    print_colored("LM Studio Integration Test Suite", BLUE)
    print_colored("=" * 60, BLUE)
    
    print(f"\nConfiguration:")
    print(f"  LLM Provider: {os.getenv('LLM_PROVIDER', 'openai')}")
    print(f"  LLM Model: {os.getenv('LLM_MODEL', 'qwen2.5-8b')}")
    print(f"  LLM Base URL: {os.getenv('LLM_BASE_URL', 'http://localhost:1234/v1')}")
    print(f"  Environment: {os.getenv('ENVIRONMENT', 'development')}")
    
    # Track test results
    results = {
        "LM Studio Server": test_lmstudio_server(),
        "OpenAI Compatibility": False,
        "Streaming": False,
        "LangChain Integration": None,
        "RAG Chain": None,
        "Compliance Agent": None,
        "Performance": False
    }
    
    # Only run other tests if server is running
    if results["LM Studio Server"]:
        results["OpenAI Compatibility"] = test_openai_compatibility()
        results["Streaming"] = test_streaming()
        results["LangChain Integration"] = test_langchain_integration()
        
        # Run async tests
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            results["RAG Chain"] = loop.run_until_complete(test_rag_chain())
        finally:
            loop.close()
        
        results["Compliance Agent"] = test_compliance_agent()
        results["Performance"] = test_performance()
    
    # Print summary
    print_colored("\n" + "=" * 60, BLUE)
    print_colored("Test Summary", BLUE)
    print_colored("=" * 60, BLUE)
    
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)
    total = len(results)
    
    for test_name, result in results.items():
        if result is True:
            print_colored(f"✓ {test_name}", GREEN)
        elif result is False:
            print_colored(f"✗ {test_name}", RED)
        else:
            print_colored(f"⚠ {test_name} (skipped)", YELLOW)
    
    print(f"\nResults: {passed}/{total} passed, {failed} failed, {skipped} skipped")
    
    if failed == 0 and passed > 0:
        print_colored("\n✅ All tests passed! LM Studio integration is working.", GREEN)
        return 0
    elif results["LM Studio Server"] is False:
        print_colored("\n❌ LM Studio server is not running. Please start it first.", RED)
        print_colored("\nQuick Start Instructions:", YELLOW)
        print("1. Open LM Studio application")
        print("2. Download Qwen2.5-8B-Instruct model (bf16 variant)")
        print("3. Go to 'Local Server' tab")
        print("4. Select the model and click 'Start Server'")
        print("5. Run this test again")
        return 1
    else:
        print_colored(f"\n❌ {failed} tests failed. Please check the errors above.", RED)
        return 1

if __name__ == "__main__":
    sys.exit(main())