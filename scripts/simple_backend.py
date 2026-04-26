#!/usr/bin/env python3
"""Simple FastAPI backend for testing"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import asyncio
import json
import sys
import os

# Add config directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'config'))
from config_manager import get_config

# Load configuration
config = get_config()

app = FastAPI(title="LangChain Compliance Assistant API")

# Enable CORS with configuration
cors_config = config.get_cors_config()
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_config.get("allowed_origins", ["*"]),
    allow_credentials=True,
    allow_methods=cors_config.get("allowed_methods", ["*"]),
    allow_headers=cors_config.get("allowed_headers", ["*"]),
)

# LLM Configuration
llm_config = config.get_llm_config()
LLM_API_BASE = f"{config.get_url('llm')}/v1"

class AttachmentInfo(BaseModel):
    filename: str
    size: int
    type: str
    purpose: str

class ChatRequest(BaseModel):
    message: str
    attachments: list[AttachmentInfo] = []
    
class ChatResponse(BaseModel):
    response: str
    knowledge_base_updated: bool = False
    files_processed: int = 0
    
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "langchain-backend"}

@app.get("/")
async def root():
    return {"message": "LangChain Compliance Assistant API", "docs": "/docs"}

@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Simple chat endpoint that calls local LLM"""
    try:
        # 处理附件信息
        knowledge_base_files = [att for att in request.attachments if att.purpose == "knowledge_base"]
        business_context_files = [att for att in request.attachments if att.purpose == "business_context"]
        
        # 构建提示词
        prompt = request.message
        
        # 如果有业务上下文附件，添加到提示词中
        if business_context_files:
            prompt += "\n\n附件信息："
            for att in business_context_files:
                prompt += f"\n- 文件: {att.filename} (大小: {att.size} bytes, 类型: {att.type})"
            prompt += "\n\n请基于这些附件信息来回答用户的问题。"
        
        # 如果有知识库更新附件，记录日志（实际实现中会调用知识库更新API）
        knowledge_base_updated = False
        if knowledge_base_files:
            print(f"Knowledge base update requested for files: {[att.filename for att in knowledge_base_files]}")
            # TODO: 实现知识库更新逻辑
            knowledge_base_updated = True
        
        async with httpx.AsyncClient() as client:
            # Call local LLM
            response = await client.post(
                f"{LLM_API_BASE}/completions",
                json={
                    "model": llm_config.get("model_name", "qwen3-8b-mlx"),
                    "prompt": prompt,
                    "max_tokens": llm_config.get("max_tokens", 1000),
                    "temperature": llm_config.get("temperature", 0.7)
                },
                timeout=llm_config.get("timeout", 60)
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Extract text from response
            if "choices" in result and len(result["choices"]) > 0:
                text = result["choices"][0].get("text", "No response")
            else:
                text = "No response from model"
                
            return ChatResponse(
                response=text,
                knowledge_base_updated=knowledge_base_updated,
                files_processed=len(request.attachments)
            )
            
    except httpx.RequestError as e:
        print(f"LLM service error: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=503, detail=f"LLM service error: {type(e).__name__}: {str(e)}")
    except Exception as e:
        print(f"General error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/models")
async def list_models():
    """List available models"""
    return {
        "models": [
            {"id": "qwen3-8b-mlx", "name": "Qwen3 8B (MLX)", "available": True}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    import sys
    
    # Get port from config or command line
    if "--port" in sys.argv:
        port = int(sys.argv[sys.argv.index("--port") + 1])
    else:
        port = config.get_port("backend")
    
    print(f"Starting backend on port {port}")
    print(f"Configuration: {config.get_environment()}")
    print(f"LLM URL: {LLM_API_BASE}")
    
    uvicorn.run(app, host="0.0.0.0", port=port)