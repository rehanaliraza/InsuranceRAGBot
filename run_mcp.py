#!/usr/bin/env python3
"""
Run script for the MCP-based Insurance RAG Bot
"""
import os
import sys
import uvicorn
from config import API_HOST, API_PORT

# Add the current directory to path if not already there
if os.path.abspath(os.path.dirname(__file__)) not in sys.path:
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def main():
    print("Starting Insurance RAG Bot with MCP architecture...")
    print(f"Server will be available at http://{API_HOST if API_HOST != '0.0.0.0' else 'localhost'}:{API_PORT}")
    uvicorn.run("app.main_mcp:app", host=API_HOST, port=API_PORT, reload=True)

if __name__ == "__main__":
    main() 