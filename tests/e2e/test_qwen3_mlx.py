#!/usr/bin/env python3
"""Test script for Qwen3-8B MLX model server"""

import requests
import json

BASE_URL = "http://localhost:8001"

print("Testing Qwen3-8B MLX Server...")
print("=" * 50)

# Test 1: Check models
print("\n1. Available models:")
try:
    response = requests.get(f"{BASE_URL}/v1/models")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        models = response.json()
        print(f"Models: {json.dumps(models, indent=2)}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Try completion
print("\n2. Testing text completion:")
try:
    response = requests.post(
        f"{BASE_URL}/v1/completions",
        json={
            "model": "mlx_qwen3_converted",
            "prompt": "Hello, my name is",
            "max_tokens": 50,
            "temperature": 0.7
        }
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {result.get('choices', [{}])[0].get('text', 'No text')}")
    else:
        print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

# Test 3: Try chat completion  
print("\n3. Testing chat completion:")
try:
    response = requests.post(
        f"{BASE_URL}/v1/chat/completions",
        json={
            "model": "mlx_qwen3_converted",
            "messages": [
                {"role": "user", "content": "Hello, how are you?"}
            ],
            "max_tokens": 50,
            "temperature": 0.7
        }
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {result.get('choices', [{}])[0].get('message', {}).get('content', 'No content')}")
    else:
        print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 50)
print("Server Info:")
print(f"URL: {BASE_URL}")
print("To use in .env file:")
print("  LLM_PROVIDER=openai")
print("  LLM_MODEL=mlx_qwen3_converted")
print("  OPENAI_API_KEY=not-required")
print(f"  OPENAI_API_BASE={BASE_URL}/v1")