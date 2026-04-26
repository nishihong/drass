#!/bin/bash

VENV_DIR="/home/qwkj/drass/venv"
BASE_DIR="/home/qwkj/drass"

# Activate virtual environment
source "$VENV_DIR/bin/activate"

echo "Installing dependencies with $(which pip)..."

# Core dependencies
pip install --upgrade pip
pip install wheel setuptools

# FastAPI and server
pip install fastapi uvicorn[standard] python-multipart aiofiles

# Authentication and security
pip install passlib[bcrypt] python-jose[cryptography] python-dotenv

# Database
pip install sqlalchemy psycopg2-binary asyncpg redis

# LangChain and AI
pip install langchain langchain-community langchain-openai openai tiktoken

# Vector store
pip install chromadb sentence-transformers

# HTTP and async
pip install httpx websockets

# Document processing
pip install pypdf python-docx openpyxl beautifulsoup4 lxml

# If requirements.txt exists, install from it
if [ -f "$BASE_DIR/services/main-app/requirements.txt" ]; then
    echo "Installing from requirements.txt..."
    pip install -r "$BASE_DIR/services/main-app/requirements.txt"
fi

echo "Dependencies installed successfully"
