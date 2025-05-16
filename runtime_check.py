#!/usr/bin/env python3
"""
Runtime check script to verify that the Insurance RAG Bot environment is set up correctly
"""
import os
import sys
import traceback

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def check_env_vars():
    """Check if environment variables are set up correctly"""
    print("Checking environment variables...")
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ ERROR: OPENAI_API_KEY not found in .env file")
        print("  Please add your OpenAI API key to the .env file")
        return False
    elif api_key == "your_openai_api_key_here":
        print("❌ ERROR: OPENAI_API_KEY has not been changed from default value")
        print("  Please update it with your actual OpenAI API key")
        return False
    else:
        print("✅ OPENAI_API_KEY found")
    
    return True

def check_imports():
    """Check if required packages are installed correctly"""
    print("\nChecking imports...")
    
    try:
        from langchain_openai import OpenAIEmbeddings
        print("✅ langchain_openai imported successfully")
    except ImportError as e:
        print(f"❌ ERROR: Failed to import langchain_openai: {e}")
        return False
    
    try:
        from langchain_community.vectorstores import Chroma
        print("✅ langchain_community.vectorstores imported successfully")
    except ImportError as e:
        print(f"❌ ERROR: Failed to import langchain_community.vectorstores: {e}")
        return False
    
    try:
        from langchain_core.prompts import ChatPromptTemplate
        print("✅ langchain_core.prompts imported successfully")
    except ImportError as e:
        print(f"❌ ERROR: Failed to import langchain_core.prompts: {e}")
        return False

    try:
        from app.utils.document_processor import process_documents
        print("✅ app.utils.document_processor imported successfully")
    except ImportError as e:
        print(f"❌ ERROR: Failed to import app.utils.document_processor: {e}")
        return False
    
    try:
        from app.utils.vectorstore import get_relevant_documents
        print("✅ app.utils.vectorstore imported successfully")
    except ImportError as e:
        print(f"❌ ERROR: Failed to import app.utils.vectorstore: {e}")
        return False
    
    return True

def check_document_loading():
    """Check if document loading works"""
    print("\nChecking document loading...")
    
    try:
        from app.utils.document_processor import process_documents
        docs = process_documents()
        print(f"✅ Documents processed successfully ({len(docs)} chunks)")
        return True
    except Exception as e:
        print(f"❌ ERROR: Failed to process documents: {e}")
        traceback.print_exc()
        return False

def check_embeddings():
    """Check if embeddings creation works"""
    print("\nChecking embeddings creation...")
    
    try:
        from langchain_openai import OpenAIEmbeddings
        from config import OPENAI_API_KEY
        
        embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        result = embeddings.embed_query("Test query")
        
        if len(result) > 0:
            print(f"✅ Embeddings created successfully (vector length: {len(result)})")
            return True
        else:
            print("❌ ERROR: Embeddings vector is empty")
            return False
    except Exception as e:
        print(f"❌ ERROR: Failed to create embeddings: {e}")
        traceback.print_exc()
        return False

def check_vectorstore():
    """Check if vectorstore creation works"""
    print("\nChecking vectorstore...")
    
    try:
        from app.utils.vectorstore import load_vectorstore
        vectorstore = load_vectorstore()
        print("✅ Vectorstore loaded/created successfully")
        return True
    except Exception as e:
        print(f"❌ ERROR: Failed to load/create vectorstore: {e}")
        traceback.print_exc()
        return False

def run_simple_query():
    """Run a simple query against the vectorstore"""
    print("\nRunning a simple query...")
    
    try:
        from app.utils.vectorstore import get_relevant_documents
        docs = get_relevant_documents("What is health insurance?")
        print(f"✅ Query returned {len(docs)} relevant documents")
        return True
    except Exception as e:
        print(f"❌ ERROR: Failed to run query: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all checks"""
    print("=== INSURANCE RAG BOT RUNTIME CHECK ===\n")
    
    checks = [
        check_env_vars,
        check_imports,
        check_document_loading,
        check_embeddings,
        check_vectorstore,
        run_simple_query
    ]
    
    passed = 0
    for check in checks:
        if check():
            passed += 1
    
    print(f"\nCheck complete: {passed}/{len(checks)} checks passed")
    
    if passed == len(checks):
        print("\n✅ All checks passed! Your system is ready to run.")
        print("  You can start the application with:")
        print("  - python3 simple_app.py      # Simple version")
        print("  - python3 start.py           # Full multi-agent version")
        return 0
    else:
        print("\n❌ Some checks failed. Please fix the issues before running the application.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 