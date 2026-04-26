#!/usr/bin/env python3
"""
Test MLX-LM Server setup for Qwen models
"""

import subprocess
import time
import requests
import json

def test_mlx_server():
    """Test MLX-LM server with a small model"""
    
    print("Starting MLX-LM Server test...")
    print("-" * 50)
    
    # Start the server with a small model for testing
    model = "mlx-community/Qwen2.5-3B-Instruct-4bit"  # Smaller model for testing
    port = 8001
    
    print(f"Starting server with model: {model}")
    print(f"Server will be available at: http://localhost:{port}/v1")
    print("")
    
    # Start server in background
    server_process = subprocess.Popen([
        "python", "-m", "mlx_lm.server",
        "--model", model,
        "--host", "0.0.0.0",
        "--port", str(port),
        "--trust-remote-code"
    ])
    
    print("Waiting for server to start (this may take a minute for first download)...")
    time.sleep(10)  # Give server time to start
    
    # Test the API
    try:
        # Test models endpoint
        response = requests.get(f"http://localhost:{port}/v1/models")
        if response.status_code == 200:
            print("✅ Server is running!")
            print(f"Available models: {response.json()}")
        else:
            print(f"❌ Server test failed: {response.status_code}")
            
        # Test chat completion
        print("\nTesting chat completion...")
        chat_response = requests.post(
            f"http://localhost:{port}/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json={
                "model": "default",
                "messages": [
                    {"role": "user", "content": "Say hello in Chinese"}
                ],
                "max_tokens": 50,
                "temperature": 0.7
            }
        )
        
        if chat_response.status_code == 200:
            result = chat_response.json()
            print("✅ Chat completion works!")
            print(f"Response: {result['choices'][0]['message']['content']}")
        else:
            print(f"❌ Chat test failed: {chat_response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Please check if it's running.")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Stop the server
        print("\nStopping server...")
        server_process.terminate()
        server_process.wait()
        print("Server stopped.")
    
    print("\n" + "=" * 50)
    print("To use MLX-LM Server in production:")
    print("1. Start server: mlx_lm.server --model mlx-community/Qwen2.5-7B-Instruct-4bit --port 8001")
    print("2. Update .env file:")
    print("   LLM_PROVIDER=openai")
    print("   LLM_MODEL=default")
    print("   OPENAI_API_KEY=not-required")
    print("   OPENAI_API_BASE=http://localhost:8001/v1")

if __name__ == "__main__":
    test_mlx_server()