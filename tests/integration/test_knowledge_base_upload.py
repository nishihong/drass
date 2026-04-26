#!/usr/bin/env python3
"""
Test script for knowledge base document upload functionality
"""

import requests
import json
import time
import sys
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"

# Test colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
NC = '\033[0m'  # No Color

def print_status(message, color=NC):
    print(f"{color}{message}{NC}")

def check_service(url, name):
    """Check if a service is running"""
    try:
        response = requests.get(f"{url}/health", timeout=5)
        if response.status_code == 200:
            print_status(f"✓ {name} is running at {url}", GREEN)
            return True
        else:
            print_status(f"✗ {name} returned status {response.status_code}", RED)
            return False
    except requests.exceptions.RequestException as e:
        print_status(f"✗ {name} is not accessible at {url}: {str(e)}", RED)
        return False

def create_test_document():
    """Create a test document for upload"""
    test_file = Path("test_document.txt")
    content = """
    # Test Document for Knowledge Base
    
    This is a test document to verify the knowledge base update functionality.
    
    ## Key Information
    - Document Type: Test
    - Purpose: Knowledge Base Update
    - Content: Sample compliance information
    
    ## Compliance Requirements
    1. Data must be encrypted at rest
    2. Access logs must be maintained
    3. Regular audits are required
    
    ## Test Data
    This document contains test data for verifying the upload and processing pipeline.
    """
    
    test_file.write_text(content)
    print_status(f"Created test document: {test_file}", BLUE)
    return test_file

def test_document_upload_api():
    """Test the document upload API directly"""
    print_status("\n=== Testing Document Upload API ===", BLUE)
    
    # Create test document
    test_file = create_test_document()
    
    try:
        # Test without authentication (should fail)
        print_status("\n1. Testing upload without authentication...", YELLOW)
        with open(test_file, 'rb') as f:
            files = {'file': ('test_document.txt', f, 'text/plain')}
            data = {
                'auto_process': 'true',
                'tags': 'test,knowledge_base'
            }
            response = requests.post(
                f"{BASE_URL}/api/v1/documents/upload",
                files=files,
                data=data
            )
        
        if response.status_code == 401:
            print_status("✓ Correctly requires authentication", GREEN)
        else:
            print_status(f"Response: {response.status_code} - {response.text[:200]}", YELLOW)
        
        # Test with mock authentication
        print_status("\n2. Testing upload with mock authentication...", YELLOW)
        
        # First, try to get a test token (if auth endpoint exists)
        auth_response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"username": "test@example.com", "password": "test123"}
        )
        
        if auth_response.status_code == 200:
            token = auth_response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            
            with open(test_file, 'rb') as f:
                files = {'file': ('test_document.txt', f, 'text/plain')}
                data = {
                    'auto_process': 'true',
                    'tags': 'test,knowledge_base'
                }
                response = requests.post(
                    f"{BASE_URL}/api/v1/documents/upload",
                    files=files,
                    data=data,
                    headers=headers
                )
            
            if response.status_code == 200:
                print_status("✓ Document uploaded successfully", GREEN)
                doc_data = response.json()
                print_status(f"  Document ID: {doc_data.get('id')}", BLUE)
                print_status(f"  Status: {doc_data.get('status')}", BLUE)
                return doc_data.get('id')
            else:
                print_status(f"✗ Upload failed: {response.status_code} - {response.text[:200]}", RED)
        else:
            print_status("Authentication endpoint not available, skipping authenticated test", YELLOW)
            
    except Exception as e:
        print_status(f"✗ Error during testing: {str(e)}", RED)
    finally:
        # Clean up test file
        if test_file.exists():
            test_file.unlink()
            print_status("Cleaned up test document", BLUE)
    
    return None

def test_knowledge_base_update():
    """Test if documents are being added to the knowledge base"""
    print_status("\n=== Testing Knowledge Base Integration ===", BLUE)
    
    # Check if vector store is accessible
    print_status("\n1. Checking ChromaDB vector store...", YELLOW)
    try:
        response = requests.get("http://localhost:8005/api/v1")
        if response.status_code == 200:
            print_status("✓ ChromaDB is accessible", GREEN)
        else:
            print_status(f"✗ ChromaDB returned status {response.status_code}", RED)
    except Exception as e:
        print_status(f"✗ ChromaDB not accessible: {str(e)}", RED)
    
    # Check if embedding service is running
    print_status("\n2. Checking Embedding Service...", YELLOW)
    try:
        response = requests.get("http://localhost:8002/health")
        if response.status_code == 200:
            print_status("✓ Embedding service is running", GREEN)
        else:
            print_status(f"✗ Embedding service returned status {response.status_code}", RED)
    except Exception as e:
        print_status(f"✗ Embedding service not accessible: {str(e)}", RED)
    
    # Test embedding generation
    print_status("\n3. Testing embedding generation...", YELLOW)
    try:
        response = requests.post(
            "http://localhost:8002/embed",
            json={"texts": ["This is a test sentence for embedding."]}
        )
        if response.status_code == 200:
            embeddings = response.json().get("embeddings", [])
            if embeddings and len(embeddings[0]) > 0:
                print_status(f"✓ Embedding generated successfully (dimension: {len(embeddings[0])})", GREEN)
            else:
                print_status("✗ Empty embeddings returned", RED)
        else:
            print_status(f"✗ Embedding generation failed: {response.status_code}", RED)
    except Exception as e:
        print_status(f"✗ Error testing embeddings: {str(e)}", RED)

def test_chat_with_knowledge():
    """Test if chat can access knowledge base"""
    print_status("\n=== Testing Chat with Knowledge Base ===", BLUE)
    
    test_queries = [
        "What are the compliance requirements mentioned in the documents?",
        "Tell me about data encryption requirements",
        "What audit requirements are documented?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print_status(f"\n{i}. Testing query: {query[:50]}...", YELLOW)
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/chat",
                json={"message": query}
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get("response", "")[:200]
                print_status(f"✓ Got response: {answer}...", GREEN)
                
                # Check if knowledge base was used
                if result.get("knowledge_base_used"):
                    print_status("  ✓ Knowledge base was accessed", GREEN)
                else:
                    print_status("  ⚠ Knowledge base may not have been used", YELLOW)
            else:
                print_status(f"✗ Query failed: {response.status_code}", RED)
                
        except Exception as e:
            print_status(f"✗ Error during query: {str(e)}", RED)

def main():
    print_status("=" * 60, BLUE)
    print_status("Knowledge Base Upload Test Suite", BLUE)
    print_status("=" * 60, BLUE)
    
    # Check services
    print_status("\n=== Checking Services ===", BLUE)
    services_ok = True
    
    services_ok &= check_service(BASE_URL, "Backend API")
    services_ok &= check_service("http://localhost:8001", "LLM Server")
    services_ok &= check_service("http://localhost:8002", "Embedding Service")
    services_ok &= check_service("http://localhost:8005", "ChromaDB")
    
    if not services_ok:
        print_status("\n⚠ Some services are not running. Please start all services first:", YELLOW)
        print_status("  ./start-full-langchain.sh", YELLOW)
        return
    
    # Run tests
    doc_id = test_document_upload_api()
    test_knowledge_base_update()
    
    # Test chat functionality if document was uploaded
    if doc_id:
        print_status("\nWaiting 5 seconds for document processing...", YELLOW)
        time.sleep(5)
        test_chat_with_knowledge()
    
    print_status("\n" + "=" * 60, BLUE)
    print_status("Test Suite Completed", BLUE)
    print_status("=" * 60, BLUE)
    
    print_status("\n💡 To test via UI:", YELLOW)
    print_status(f"  1. Open {FRONTEND_URL}", NC)
    print_status("  2. Click on 'Upload' button", NC)
    print_status("  3. Select a file and choose 'knowledge_base' as purpose", NC)
    print_status("  4. Submit and verify the file is processed", NC)

if __name__ == "__main__":
    main()