#!/usr/bin/env python3
"""
Script to print all content from the ChromaDB vectorstore
"""
import os
import sys
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from config import OPENAI_API_KEY, VECTOR_DB_PATH

def print_chroma_content():
    """Print all documents stored in ChromaDB"""
    try:
        # Set up ChromaDB
        persist_directory = os.path.join(VECTOR_DB_PATH, "chroma_db")
        collection_name = "insurance_docs"
        embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        
        # Load the vectorstore
        vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings,
            collection_name=collection_name
        )
        
        print(f"Loading ChromaDB from {persist_directory}")
        
        # Get the collection
        collection = vectorstore._collection
        
        # Get all documents
        result = collection.get()
        
        # Print collection stats
        print(f"\nTotal documents in collection: {len(result['ids'])}")
        print(f"Collection name: {collection_name}")
        
        # Print all documents with their metadata
        print("\n===== DOCUMENTS IN CHROMADB =====")
        
        for i, (doc_id, document, metadata) in enumerate(zip(result['ids'], result['documents'], result['metadatas'])):
            print(f"\n----- Document {i+1} -----")
            print(f"ID: {doc_id}")
            print(f"Source: {metadata.get('source', 'unknown')}")
            print(f"Content (first 500 chars): {document[:500]}..." if len(document) > 500 else f"Content: {document}")
            print("-" * 50)
        
        return True
    except Exception as e:
        print(f"Error accessing ChromaDB: {e}")
        return False

if __name__ == "__main__":
    print_chroma_content()
