#!/usr/bin/env python3
"""
Simple API server for testing document upload functionality
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import uuid
import json
from datetime import datetime
from typing import List, Dict, Any
import uvicorn

# Create FastAPI app
app = FastAPI(title="Simple Document API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory storage for testing
documents_db = []

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/v1/documents/test")
async def get_documents_test():
    """Get all documents (no auth required for testing)"""
    return documents_db

@app.post("/api/v1/documents/upload-test")
async def upload_document_test(file: UploadFile = File(...)):
    """Upload a document (no auth required for testing)"""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Create document record
        doc_id = str(uuid.uuid4())
        content = await file.read()
        
        # Save file to uploads directory
        upload_dir = "/home/qwkj/drass/data/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, f"{doc_id}_{file.filename}")
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Create document record
        document = {
            "id": doc_id,
            "name": file.filename,
            "type": file.filename.split(".")[-1].lower() if "." in file.filename else "unknown",
            "size": len(content),
            "status": "uploaded",
            "metadata": {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "tags": []
        }
        
        # Add to in-memory database
        documents_db.append(document)
        
        return document
        
    except Exception as e:
        print(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/")
async def root():
    return {
        "message": "Simple Document API",
        "endpoints": {
            "health": "/health",
            "documents": "/api/v1/documents/test",
            "upload": "/api/v1/documents/upload-test"
        }
    }

if __name__ == "__main__":
    print("Starting Simple Document API on port 8888...")
    uvicorn.run(app, host="0.0.0.0", port=8888)