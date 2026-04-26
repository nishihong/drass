#!/usr/bin/env python3
"""
vLLM Integration Test for Drass Compliance Assistant
Tests the complete integration with vLLM serving Qwen2.5-8B model (bf16)
"""

import os
import sys
import time
import requests
import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv

# Add project to path
sys.path.insert(0, str(Path(__file__).parent / "services" / "main-app"))

# Load environment variables
load_dotenv(".env.vllm")

# Color codes for output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

def print_colored(message: str, color: str = NC):
    """Print colored message"""
    print(f"{color}{message}{NC}")

def test_vllm_server():
    """Test if vLLM server is running"""
    print_colored("\n1. Testing vLLM Server Status...", BLUE)
    
    base_url = os.getenv("VLLM_API_URL", "http://localhost:8001/v1")
    
    try:
        # Test models endpoint
        response = requests.get(f"{base_url}/models", timeout=5)
        
        if response.status_code == 200:
            models = response.json()
            print_colored("✓ vLLM server is running", GREEN)
            print(f"   Available models: {models.get('data', [])}")
            
            # Check for our specific model
            model_names = [m.get('id') for m in models.get('data', [])]
            if 'qwen2.5-8b' in model_names:
                print_colored("✓ Qwen2.5-8B model is loaded", GREEN)
            else:
                print_colored("⚠ Qwen2.5-8B model not found in available models", YELLOW)
            
            return True
        else:
            print_colored(f"✗ Server returned status {response.status_code}", RED)
            return False
            
    except requests.exceptions.ConnectionError:
        print_colored("✗ Cannot connect to vLLM server", RED)
        print_colored("   Please start vLLM server:", YELLOW)
        print("   1. Run: ./scripts/deploy_vllm.sh")
        print("   2. Activate venv: source venv_vllm/bin/activate")
        print("   3. Start server: ./start_vllm.sh")
        return False
    except Exception as e:
        print_colored(f"✗ Error: {e}", RED)
        return False

def test_openai_compatibility():
    """Test OpenAI API compatibility"""
    print_colored("\n2. Testing OpenAI API Compatibility...", BLUE)
    
    base_url = os.getenv("VLLM_API_URL", "http://localhost:8001/v1")
    
    try:
        payload = {
            "model": os.getenv("LLM_MODEL", "qwen2.5-8b"),
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'vLLM API test successful!' in exactly those words."}
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
            
            # Check usage information
            if 'usage' in result:
                usage = result['usage']
                print(f"   Tokens used: prompt={usage.get('prompt_tokens', 0)}, "
                      f"completion={usage.get('completion_tokens', 0)}, "
                      f"total={usage.get('total_tokens', 0)}")
            
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
    
    base_url = os.getenv("VLLM_API_URL", "http://localhost:8001/v1")
    
    try:
        payload = {
            "model": os.getenv("LLM_MODEL", "qwen2.5-8b"),
            "messages": [
                {"role": "user", "content": "Count from 1 to 5, one number per line."}
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
            
            tokens_received = 0
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith("data: "):
                        data = line_str[6:]
                        if data != "[DONE]":
                            try:
                                chunk = json.loads(data)
                                content = chunk['choices'][0].get('delta', {}).get('content', '')
                                if content:
                                    tokens_received += 1
                                    print(".", end="", flush=True)
                            except:
                                pass
            
            print(f"\n   Tokens streamed: {tokens_received}")
            return True
        else:
            print_colored(f"✗ Streaming failed with status {response.status_code}", RED)
            return False
            
    except Exception as e:
        print_colored(f"✗ Error testing streaming: {e}", RED)
        return False

def test_langchain_integration():
    """Test LangChain integration with vLLM"""
    print_colored("\n4. Testing LangChain Integration...", BLUE)
    
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage, SystemMessage
        
        # Create LangChain LLM instance
        llm = ChatOpenAI(
            model=os.getenv("LLM_MODEL", "qwen2.5-8b"),
            openai_api_key="not-required",  # vLLM doesn't need key
            openai_api_base=os.getenv("VLLM_API_URL", "http://localhost:8001/v1"),
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

def test_performance():
    """Test performance metrics with vLLM"""
    print_colored("\n5. Testing Performance Metrics...", BLUE)
    
    base_url = os.getenv("VLLM_API_URL", "http://localhost:8001/v1")
    
    try:
        # Test with different input sizes
        test_cases = [
            ("Short", "What is 2+2?", 10),
            ("Medium", "Explain data compliance in 50 words.", 100),
            ("Long", "Write a detailed explanation of GDPR requirements for small businesses.", 500)
        ]
        
        results = []
        
        for name, prompt, max_tokens in test_cases:
            start_time = time.time()
            
            payload = {
                "model": os.getenv("LLM_MODEL", "qwen2.5-8b"),
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": max_tokens
            }
            
            response = requests.post(
                f"{base_url}/chat/completions",
                json=payload,
                timeout=60
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                result = response.json()
                usage = result.get("usage", {})
                
                tokens_per_second = usage.get("completion_tokens", 0) / response_time if response_time > 0 else 0
                
                results.append({
                    "name": name,
                    "time": response_time,
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "tokens_per_second": tokens_per_second
                })
        
        print_colored("✓ Performance metrics collected", GREEN)
        print("\n   Performance Summary:")
        print("   " + "-" * 60)
        print(f"   {'Test':<10} {'Time(s)':<10} {'Prompt':<10} {'Output':<10} {'Tokens/s':<10}")
        print("   " + "-" * 60)
        
        for r in results:
            print(f"   {r['name']:<10} {r['time']:<10.2f} {r['prompt_tokens']:<10} "
                  f"{r['completion_tokens']:<10} {r['tokens_per_second']:<10.1f}")
        
        avg_tokens_per_sec = sum(r['tokens_per_second'] for r in results) / len(results)
        
        if avg_tokens_per_sec > 50:
            print_colored(f"\n   ✓ Excellent performance: {avg_tokens_per_sec:.1f} tokens/s", GREEN)
        elif avg_tokens_per_sec > 20:
            print_colored(f"\n   ✓ Good performance: {avg_tokens_per_sec:.1f} tokens/s", GREEN)
        elif avg_tokens_per_sec > 10:
            print_colored(f"\n   ⚠ Moderate performance: {avg_tokens_per_sec:.1f} tokens/s", YELLOW)
        else:
            print_colored(f"\n   ✗ Poor performance: {avg_tokens_per_sec:.1f} tokens/s", RED)
        
        return True
        
    except Exception as e:
        print_colored(f"✗ Error testing performance: {e}", RED)
        return False

def test_concurrent_requests():
    """Test vLLM's ability to handle concurrent requests"""
    print_colored("\n6. Testing Concurrent Request Handling...", BLUE)
    
    base_url = os.getenv("VLLM_API_URL", "http://localhost:8001/v1")
    
    try:
        import concurrent.futures
        
        def make_request(i):
            payload = {
                "model": os.getenv("LLM_MODEL", "qwen2.5-8b"),
                "messages": [{"role": "user", "content": f"What is {i} + {i}?"}],
                "temperature": 0.1,
                "max_tokens": 20
            }
            
            start = time.time()
            response = requests.post(f"{base_url}/chat/completions", json=payload, timeout=30)
            end = time.time()
            
            if response.status_code == 200:
                return True, end - start
            else:
                return False, 0
        
        num_requests = 5
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = [executor.submit(make_request, i) for i in range(num_requests)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        successful = sum(1 for success, _ in results if success)
        avg_response_time = sum(t for _, t in results) / len(results)
        
        print_colored(f"✓ Handled {successful}/{num_requests} concurrent requests", GREEN)
        print(f"   Total time: {total_time:.2f}s")
        print(f"   Average response time: {avg_response_time:.2f}s")
        print(f"   Throughput: {num_requests/total_time:.2f} requests/s")
        
        return successful == num_requests
        
    except Exception as e:
        print_colored(f"✗ Error testing concurrent requests: {e}", RED)
        return False

def test_model_info():
    """Get detailed model information from vLLM"""
    print_colored("\n7. Testing Model Information Endpoint...", BLUE)
    
    base_url = os.getenv("VLLM_API_URL", "http://localhost:8001/v1")
    
    try:
        # Test model info endpoint
        response = requests.get(f"{base_url}/models", timeout=5)
        
        if response.status_code == 200:
            models_info = response.json()
            print_colored("✓ Model information retrieved", GREEN)
            
            for model in models_info.get('data', []):
                print(f"\n   Model ID: {model.get('id')}")
                print(f"   Object: {model.get('object')}")
                print(f"   Created: {model.get('created')}")
                print(f"   Owned by: {model.get('owned_by', 'vllm')}")
                
                # Additional model details if available
                if 'root' in model:
                    print(f"   Root: {model.get('root')}")
                if 'parent' in model:
                    print(f"   Parent: {model.get('parent')}")
            
            return True
        else:
            print_colored(f"✗ Failed to get model info: {response.status_code}", RED)
            return False
            
    except Exception as e:
        print_colored(f"✗ Error getting model info: {e}", RED)
        return False

def main():
    """Run all integration tests"""
    print_colored("=" * 60, BLUE)
    print_colored("vLLM Integration Test Suite", BLUE)
    print_colored("=" * 60, BLUE)
    
    print(f"\nConfiguration:")
    print(f"  LLM Provider: {os.getenv('LLM_PROVIDER', 'vllm')}")
    print(f"  LLM Model: {os.getenv('LLM_MODEL', 'qwen2.5-8b')}")
    print(f"  vLLM API URL: {os.getenv('VLLM_API_URL', 'http://localhost:8001/v1')}")
    print(f"  Model Dtype: {os.getenv('MODEL_DTYPE', 'bfloat16')}")
    print(f"  Environment: {os.getenv('ENVIRONMENT', 'development')}")
    
    # Track test results
    results = {
        "vLLM Server": test_vllm_server(),
        "OpenAI Compatibility": False,
        "Streaming": False,
        "LangChain Integration": None,
        "Performance": False,
        "Concurrent Requests": False,
        "Model Info": False
    }
    
    # Only run other tests if server is running
    if results["vLLM Server"]:
        results["OpenAI Compatibility"] = test_openai_compatibility()
        results["Streaming"] = test_streaming()
        results["LangChain Integration"] = test_langchain_integration()
        results["Performance"] = test_performance()
        results["Concurrent Requests"] = test_concurrent_requests()
        results["Model Info"] = test_model_info()
    
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
        print_colored("\n✅ All tests passed! vLLM integration is working.", GREEN)
        print_colored("\nvLLM provides high-performance inference with:", GREEN)
        print("  - Continuous batching for optimal throughput")
        print("  - PagedAttention for efficient memory usage")
        print("  - Support for bf16 precision")
        print("  - OpenAI-compatible API")
        return 0
    elif results["vLLM Server"] is False:
        print_colored("\n❌ vLLM server is not running. Please start it first.", RED)
        print_colored("\nQuick Start Instructions:", YELLOW)
        print("1. Run deployment script: ./scripts/deploy_vllm.sh")
        print("2. Activate environment: source venv_vllm/bin/activate")
        print("3. Download model: python3 download_model.py")
        print("4. Start server: ./start_vllm.sh")
        print("5. Run this test again")
        return 1
    else:
        print_colored(f"\n❌ {failed} tests failed. Please check the errors above.", RED)
        return 1

if __name__ == "__main__":
    sys.exit(main())