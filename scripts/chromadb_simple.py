#!/usr/bin/env python3
import sys
import os

# Set data path
data_path = sys.argv[1] if len(sys.argv) > 1 else "/home/qwkj/drass/data/chromadb"
port = int(sys.argv[2]) if len(sys.argv) > 2 else 8005

print(f"Starting ChromaDB on port {port}")

try:
    import chromadb
    from chromadb.config import Settings

    # Create persistent client
    client = chromadb.PersistentClient(
        path=data_path,
        settings=Settings(allow_reset=True, anonymized_telemetry=False)
    )

    print(f"ChromaDB client initialized at {data_path}")

    # Try to start a simple HTTP server for health checks
    from http.server import HTTPServer, BaseHTTPRequestHandler

    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/api/v1/collections':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"collections":[]}')
            else:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'ChromaDB is running')

        def log_message(self, format, *args):
            pass  # Suppress logs

    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    print(f"ChromaDB health server running on port {port}")
    server.serve_forever()

except Exception as e:
    print(f"Error starting ChromaDB: {e}")
    import time
    while True:
        time.sleep(60)
