#!/usr/bin/env python3
import os
import sys

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Now import the create_vectorstore function
from app.utils.vectorstore import create_vectorstore

if __name__ == "__main__":
    print("Initializing vectorstore...")
    try:
        vectorstore = create_vectorstore()
        print("Vectorstore initialization complete.")
    except Exception as e:
        print(f"Error initializing vectorstore: {e}") 