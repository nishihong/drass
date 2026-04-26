#!/bin/bash

# Start Local Document Processor (Docker-free fallback)

echo "Starting Local Document Processor..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Install minimal dependencies if needed
pip3 install Flask flask-cors PyPDF2 python-docx openpyxl 2>/dev/null

# Start the local processor
cd services/doc-processor
nohup python3 local_processor.py > ../../logs/doc-processor-local.log 2>&1 &
PID=$!

echo "Local Document Processor started (PID: $PID)"
echo "Check logs: tail -f logs/doc-processor-local.log"
echo "Health check: curl http://localhost:5003/health"