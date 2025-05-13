#!/usr/bin/env python3
"""
Starter script for Insurance RAG Bot that handles Python path issues
"""
import os
import sys
import traceback

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def main():
    # Verify OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        print("Error: Please set your OpenAI API key in the .env file")
        print("Example: OPENAI_API_KEY=sk-...")
        return 1

    # Create vectorstore directory if it doesn't exist
    os.makedirs("vectorstore", exist_ok=True)
    os.makedirs("app/static", exist_ok=True)

    # Initialize the vectorstore
    print("Initializing vectorstore...")
    try:
        from app.utils.vectorstore import create_vectorstore
        vectorstore = create_vectorstore()
        print("Vectorstore initialization complete!")
    except Exception as e:
        print(f"Error initializing vectorstore: {str(e)}")
        traceback.print_exc()
        return 1

    # Start the FastAPI server
    print("\nStarting the FastAPI server...")
    try:
        import uvicorn
        from app.main import app
        
        # Run the server
        uvicorn.run(app, host="0.0.0.0", port=8000)
        return 0
    except Exception as e:
        print(f"Error starting server: {str(e)}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 