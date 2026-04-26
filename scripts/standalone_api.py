#!/usr/bin/env python3
"""
Standalone simple API server for Drass
This is a completely independent server that doesn't import any app modules
"""

# CRITICAL: Exit immediately if uvicorn tries to run this as a module
if __name__ != "__main__":
    print("ERROR: standalone_api.py must be run directly, not imported!")
    import sys
    sys.exit(1)

import json
import sys
import os

# Debug information
print(f"Starting standalone_api.py...")
print(f"Python: {sys.executable}")
print(f"Script: {sys.argv[0]}")
print(f"CWD: {os.getcwd()}")

# Remove any paths that might lead to app imports
sys.path = [p for p in sys.path if 'services' not in p and 'main-app' not in p]

# Only import after cleaning path
from http.server import HTTPServer, BaseHTTPRequestHandler
import datetime

PORT = 8888

class StandaloneAPIHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        """Override to reduce noise in logs"""
        pass

    def do_GET(self):
        if self.path == '/' or self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                'status': 'ok',
                'message': 'Drass Standalone API Server',
                'timestamp': datetime.datetime.now().isoformat(),
                'note': 'This is a fallback API - main API not available'
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/api/v1/chat':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length > 0 else b'{}'

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            response = {
                'response': 'Standalone API server is running. Main backend not available.',
                'timestamp': datetime.datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == '__main__':
    print(f'Starting Standalone API server on port {PORT}...')
    print(f'Server is ready at http://localhost:{PORT}/')
    print('This is a fallback server - not the main Drass API')

    try:
        server = HTTPServer(('0.0.0.0', PORT), StandaloneAPIHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down server...')
        server.shutdown()
    except Exception as e:
        print(f'Error: {e}')
        sys.exit(1)