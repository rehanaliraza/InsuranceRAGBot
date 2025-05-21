from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from app.utils.document_processor import process_documents
from config import OPENAI_API_KEY, VECTOR_DB_PATH
import os

def create_vectorstore(documents=None, save_path=VECTOR_DB_PATH):
    """
    Create a vectorstore from documents and save it to disk
    """
    if documents is None:
        documents = process_documents()
    
    print("Creating embeddings and vectorstore...")
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    
    # Create directory if it doesn't exist
    os.makedirs(save_path, exist_ok=True)
    
    # Create and persist Chroma vectorstore
    collection_name = "knowledge_docs"
    persist_directory = os.path.join(save_path, "chroma_db")
    
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=persist_directory,
        collection_name=collection_name
    )
    
    # Explicitly persist the vectorstore
    vectorstore.persist()
    
    print(f"Vectorstore saved to {persist_directory}")
    return vectorstore

def load_vectorstore(load_path=VECTOR_DB_PATH):
    """
    Load a vectorstore from disk
    """
    try:
        persist_directory = os.path.join(load_path, "chroma_db")
        collection_name = "knowledge_docs"
        embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        
        # Load the persisted Chroma vectorstore
        vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings,
            collection_name=collection_name
        )
        
        print(f"Loaded vectorstore from {persist_directory}")
        return vectorstore
    except Exception as e:
        print(f"Vectorstore not found at {load_path} or error loading: {e}")
        print("Creating new vectorstore...")
        return create_vectorstore(save_path=load_path)
    
def get_relevant_documents(query, vectorstore=None, k=4):
    """
    Retrieve relevant documents for a query
    """
    if vectorstore is None:
        vectorstore = load_vectorstore()
    
    documents = vectorstore.similarity_search(query, k=k)
    
    # Print the chunks for debugging
    print("\n" + "="*80)
    print(f"QUERY: {query}")
    print("="*80)
    print(f"RETRIEVED {len(documents)} RELEVANT CHUNKS:")
    for i, doc in enumerate(documents):
        print(f"\nCHUNK {i+1}:")
        print(f"Source: {doc.metadata.get('source', 'unknown')}")
        print(f"Content:\n{doc.page_content[:500]}..." if len(doc.page_content) > 500 else f"Content:\n{doc.page_content}")
    print("="*80 + "\n")
    
    return documents 