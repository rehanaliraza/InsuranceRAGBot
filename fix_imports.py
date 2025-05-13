#!/usr/bin/env python3
"""
Helper script to fix imports in the project to use the latest LangChain package structure
"""
import os
import re
import glob

def update_imports(file_path):
    """Update imports in a Python file to use the latest LangChain package structure"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define import replacements
    replacements = [
        (r'from langchain\.document_loaders import (\w+)', r'from langchain_community.document_loaders import \1'),
        (r'from langchain\.vectorstores import (\w+)', r'from langchain_community.vectorstores import \1'),
        (r'from langchain\.vectorstores\.(\w+) import (\w+)', r'from langchain_community.vectorstores import \2'),
        (r'from langchain\.text_splitter import (\w+)', r'from langchain_text_splitters import \1'),
        (r'from langchain\.embeddings import (\w+)', r'from langchain_community.embeddings import \1'),
        (r'from langchain\.chat_models import (\w+)', r'from langchain_community.chat_models import \1'),
    ]
    
    # Apply replacements
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Updated imports in {file_path}")

def main():
    """Find and update Python files in the project"""
    # Find all Python files
    python_files = glob.glob('app/**/*.py', recursive=True)
    python_files.extend(glob.glob('*.py'))
    
    # Update imports in each file
    for file_path in python_files:
        update_imports(file_path)
    
    print(f"Updated imports in {len(python_files)} files")

if __name__ == "__main__":
    main() 