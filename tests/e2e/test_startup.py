#!/usr/bin/env python3
"""
Test script to understand why standalone_api.py runs app.main code
"""

import sys
import os

print("=== Python Startup Test ===")
print(f"Script name: {sys.argv[0]}")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"__file__: {__file__ if '__file__' in globals() else 'Not defined'}")
print(f"__name__: {__name__}")

print("\nPython path:")
for i, p in enumerate(sys.path):
    print(f"  {i}: {p}")

print("\nEnvironment variables:")
print(f"  PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
print(f"  PORT: {os.environ.get('PORT', 'Not set')}")

print("\nChecking if uvicorn is installed:")
try:
    import uvicorn
    print(f"  uvicorn found: {uvicorn.__file__}")

    # Check if uvicorn has any auto-discovery features
    print("\n  Checking uvicorn behavior...")
    print(f"  uvicorn.main: {hasattr(uvicorn, 'main')}")

except ImportError:
    print("  uvicorn not installed")

print("\nChecking current directory contents:")
files = os.listdir('.')
py_files = [f for f in files if f.endswith('.py')]
print(f"  Python files: {py_files[:5]}")  # Show first 5

print("\nChecking if app module exists:")
try:
    # Don't actually import it, just check if it's importable
    import importlib.util
    spec = importlib.util.find_spec("app")
    if spec:
        print(f"  app module found at: {spec.origin}")
    else:
        print("  app module not found")
except Exception as e:
    print(f"  Error checking app module: {e}")

print("\nChecking if app.main exists:")
try:
    spec = importlib.util.find_spec("app.main")
    if spec:
        print(f"  app.main module found at: {spec.origin}")
    else:
        print("  app.main module not found")
except Exception as e:
    print(f"  Error checking app.main: {e}")

print("\n=== Test Complete ===")
print("If app.main is found when running this from /home/qwkj/drass,")
print("it means Python can import it from that location.")
print("This would explain why standalone_api.py runs the main app code.")