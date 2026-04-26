#!/usr/bin/env python3
"""
Test script for LLM and Embedding integration
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv('services/main-app/.env')

def test_llm_service():
    """Test the local LLM service"""
    print("=" * 50)
    print("Testing LLM Service (Qwen3-8B-MLX)")
    print("=" * 50)
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8001/health")
        if response.status_code == 200:
            print("✅ LLM Service is healthy")
            print(f"   Response: {response.json()}")
        else:
            print("❌ LLM Service is not responding")
            return False
        
        # Test chat completion
        chat_data = {
            "model": "qwen3-8b-mlx",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What is compliance management? Answer in one sentence."}
            ],
            "max_tokens": 50
        }
        
        response = requests.post(
            "http://localhost:8001/v1/chat/completions",
            json=chat_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Chat completion successful")
            print(f"   Model response: {result['choices'][0]['message']['content']}")
            return True
        else:
            print(f"❌ Chat completion failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing LLM service: {e}")
        return False

def test_embedding_service():
    """Test the embedding service"""
    print("\n" + "=" * 50)
    print("Testing Embedding Service")
    print("=" * 50)
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8002/health")
        if response.status_code == 200:
            print("✅ Embedding Service is healthy")
            print(f"   Response: {response.json()}")
        else:
            print("❌ Embedding Service is not responding")
            return False
        
        # Test embedding generation
        embed_data = {
            "texts": ["This is a test sentence for embedding."],
            "model": "all-MiniLM-L6-v2"
        }
        
        response = requests.post(
            "http://localhost:8002/embeddings",
            json=embed_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Embedding generation successful")
            print(f"   Embedding dimension: {len(result['embeddings'][0])}")
            return True
        else:
            print(f"❌ Embedding generation failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing embedding service: {e}")
        return False

def test_langchain_integration():
    """Test basic LangChain integration"""
    print("\n" + "=" * 50)
    print("Testing LangChain Integration")
    print("=" * 50)
    
    try:
        from langchain.llms import OpenAI
        from langchain.chains import LLMChain
        from langchain.prompts import PromptTemplate
        
        # Configure LLM with local endpoint
        llm = OpenAI(
            openai_api_key="not-required",
            openai_api_base="http://localhost:8001/v1",
            model_name="qwen3-8b-mlx",
            temperature=0.7,
            max_tokens=100
        )
        
        # Create a simple chain
        prompt = PromptTemplate(
            input_variables=["topic"],
            template="Explain {topic} in simple terms:"
        )
        
        chain = LLMChain(llm=llm, prompt=prompt)
        
        # Test the chain
        result = chain.run(topic="regulatory compliance")
        
        print("✅ LangChain integration successful")
        print(f"   Chain output: {result[:200]}...")
        return True
        
    except Exception as e:
        print(f"❌ LangChain integration failed: {e}")
        return False

def main():
    """Run all tests"""
    print("\n🚀 Starting Integration Tests\n")
    
    # Test services
    llm_ok = test_llm_service()
    embed_ok = test_embedding_service()
    langchain_ok = test_langchain_integration()
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    print(f"LLM Service:        {'✅ PASS' if llm_ok else '❌ FAIL'}")
    print(f"Embedding Service:  {'✅ PASS' if embed_ok else '❌ FAIL'}")
    print(f"LangChain:          {'✅ PASS' if langchain_ok else '❌ FAIL'}")
    
    if llm_ok and embed_ok:
        print("\n✅ All services are operational!")
        print("You can now start the FastAPI backend with:")
        print("  cd services/main-app")
        print("  source venv/bin/activate")
        print("  uvicorn app.main:app --reload")
    else:
        print("\n⚠️  Some services are not working properly.")
        print("Please check the services and try again.")

if __name__ == "__main__":
    main()