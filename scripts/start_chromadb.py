import chromadb
import uvicorn
import os
import sys

# Set up ChromaDB path
chroma_path = sys.argv[1] if len(sys.argv) > 1 else "/home/qwkj/drass/data/chromadb"
port = int(sys.argv[2]) if len(sys.argv) > 2 else 8005

print(f"Starting ChromaDB on port {port} with data path: {chroma_path}")

try:
    # Try to start ChromaDB server
    from chromadb.app import app
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
except ImportError:
    # Fallback to persistent client
    print("ChromaDB app module not found, using persistent client mode")
    client = chromadb.PersistentClient(path=chroma_path)
    print(f"ChromaDB client initialized at {chroma_path}")
    print("Note: ChromaDB is running in client mode, not as a server")
    # Keep the process running
    import time
    while True:
        time.sleep(60)
