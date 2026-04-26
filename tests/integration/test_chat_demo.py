#!/usr/bin/env python3
"""
Simple demo to test the chat functionality
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"

def test_chat():
    """Test basic chat functionality"""
    print("=== Testing Chat API ===\n")
    
    # Test queries
    queries = [
        "Hello, how are you?",
        "What is compliance management?",
        "Tell me about data privacy regulations",
    ]
    
    for query in queries:
        print(f"Q: {query}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/chat",
                json={"message": query}
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get("response", "No response")
                print(f"A: {answer[:200]}...")
                
                if result.get("knowledge_base_updated"):
                    print("  ✓ Knowledge base was updated")
                if result.get("files_processed", 0) > 0:
                    print(f"  ✓ Processed {result['files_processed']} files")
            else:
                print(f"Error: {response.status_code}")
                
        except Exception as e:
            print(f"Error: {str(e)}")
        
        print("-" * 60)

def test_with_attachment():
    """Test chat with attachment information"""
    print("\n=== Testing Chat with Attachment Info ===\n")
    
    # Simulate attachment info
    request_data = {
        "message": "I've uploaded a compliance document. Can you summarize it?",
        "attachments": [
            {
                "filename": "compliance_policy.pdf",
                "size": 102400,
                "type": "application/pdf",
                "purpose": "knowledge_base"
            }
        ]
    }
    
    print(f"Request: {request_data['message']}")
    print(f"Attachment: {request_data['attachments'][0]['filename']} ({request_data['attachments'][0]['purpose']})")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/chat",
            json=request_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result.get('response', 'No response')[:300]}...")
            
            if result.get("knowledge_base_updated"):
                print("\n✅ Knowledge base update was triggered")
            else:
                print("\n⚠️  Knowledge base update not implemented (using simple backend)")
                
        else:
            print(f"Error: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

def main():
    print("=" * 60)
    print("Chat API Demo")
    print("=" * 60)
    
    # Check service
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Backend is running\n")
        else:
            print("❌ Backend is not healthy\n")
            return
    except:
        print("❌ Cannot connect to backend\n")
        return
    
    # Run tests
    test_chat()
    test_with_attachment()
    
    print("\n" + "=" * 60)
    print("Demo Complete")
    print("=" * 60)
    print("\n💡 Note: Full knowledge base functionality requires:")
    print("  - Embedding service (port 8002)")
    print("  - ChromaDB vector store (port 8005)")
    print("  - Main FastAPI backend with LangChain integration")
    print("\nCurrent setup is using simplified backend for testing.")

if __name__ == "__main__":
    main()