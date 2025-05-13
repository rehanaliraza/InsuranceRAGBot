from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
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
    vectorstore = FAISS.from_documents(documents, embeddings)
    
    # Create directory if it doesn't exist
    os.makedirs(save_path, exist_ok=True)
    
    # Save the vectorstore using FAISS's built-in save_local method
    save_file_path = os.path.join(save_path, "faiss_index")
    vectorstore.save_local(save_file_path)
    
    print(f"Vectorstore saved to {save_file_path}")
    return vectorstore

def load_vectorstore(load_path=VECTOR_DB_PATH):
    """
    Load a vectorstore from disk
    """
    try:
        save_file_path = os.path.join(load_path, "faiss_index")
        embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
        vectorstore = FAISS.load_local(save_file_path, embeddings)
        print(f"Loaded vectorstore from {save_file_path}")
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
    return documents 