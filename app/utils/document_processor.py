from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import CHUNK_SIZE, CHUNK_OVERLAP
import os

def load_documents(data_dir="app/data"):
    """
    Load documents from the specified directory
    """
    # Load regular insurance documents
    main_loader = DirectoryLoader(data_dir, glob="**/*.txt", loader_cls=TextLoader)
    documents = main_loader.load()
    
    # Load sales materials if they exist
    sales_dir = os.path.join(data_dir, "sales")
    if os.path.exists(sales_dir):
        sales_loader = DirectoryLoader(sales_dir, glob="**/*.txt", loader_cls=TextLoader)
        sales_documents = sales_loader.load()
        documents.extend(sales_documents)
        print(f"Loaded {len(sales_documents)} sales documents")
    
    print(f"Loaded {len(documents)} total documents")
    return documents

def chunk_documents(documents):
    """
    Split documents into chunks with specified size and overlap
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks")
    return chunks

def process_documents(data_dir="app/data"):
    """
    Load and process documents from the data directory
    """
    documents = load_documents(data_dir)
    chunks = chunk_documents(documents)
    return chunks 