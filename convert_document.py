#!/usr/bin/env python3
"""
Script to convert a document to text and initialize the vectorstore.
This script is used to convert PDF, XLSX, or CSV files to cleaned text,
save them to the app/data directory, and then initialize the vectorstore
to include the new text files.
"""
import os
import sys
import argparse
import requests
from app.utils.document_converter import save_as_text_file
from app.utils.vectorstore import create_vectorstore
from config import API_HOST, API_PORT

# Add the current directory to path if not already there
if os.path.abspath(os.path.dirname(__file__)) not in sys.path:
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def convert_and_initialize(file_path):
    """
    Convert a document to text and initialize the vectorstore.
    
    Args:
        file_path: Path to the document file
    """
    print(f"Converting document: {file_path}")
    
    # Check if file exists
    if not os.path.isfile(file_path):
        print(f"Error: File not found: {file_path}")
        return False
        
    # Get file extension
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    # Check supported formats
    supported_formats = ['.pdf', '.xlsx', '.xls', '.csv']
    if ext not in supported_formats:
        print(f"Error: Unsupported file format: {ext}. Supported formats are {', '.join(supported_formats)}")
        return False
    
    # Use data directory for output
    output_dir = "app/data"
    
    # Convert document to text
    text_path = save_as_text_file(file_path, output_dir)
    
    if not text_path:
        print("Error: Failed to convert document")
        return False
    
    print(f"Document converted to text file: {text_path}")
    print("Initializing vectorstore...")
    
    # Initialize the vectorstore
    try:
        create_vectorstore()
        print("Vectorstore initialized successfully")
        return True
    except Exception as e:
        print(f"Error initializing vectorstore: {e}")
        return False

def convert_via_api(file_path):
    """
    Use the API to convert a document and initialize the vectorstore.
    
    Args:
        file_path: Path to the document file
    """
    try:
        # Convert document
        print(f"Converting document via API: {file_path}")
        convert_url = f"http://{API_HOST}:{API_PORT}/api/convert-document"
        response = requests.post(convert_url, json={"file_path": file_path})
        response.raise_for_status()
        
        # Initialize vectorstore
        print("Initializing vectorstore via API...")
        init_url = f"http://{API_HOST}:{API_PORT}/api/initialize"
        response = requests.post(init_url)
        response.raise_for_status()
        
        print("Document converted and vectorstore initialized successfully")
        return True
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        print(f"Response: {e.response.text if hasattr(e, 'response') and e.response else 'No response'}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Convert documents to text and initialize the vectorstore")
    parser.add_argument("file_path", help="Path to the document file (PDF, XLSX, CSV)")
    parser.add_argument("--api", action="store_true", help="Use the API instead of direct conversion")
    
    args = parser.parse_args()
    
    if args.api:
        # Use the API to convert the document and initialize the vectorstore
        success = convert_via_api(args.file_path)
    else:
        # Convert document directly and initialize vectorstore
        success = convert_and_initialize(args.file_path)
    
    if success:
        print("✓ Process completed successfully")
        return 0
    else:
        print("✗ Process failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
