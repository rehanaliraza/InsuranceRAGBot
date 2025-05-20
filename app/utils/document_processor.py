from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import CHUNK_SIZE, CHUNK_OVERLAP
import os

def load_documents(data_dir="app/data"):
    """
    Load documents from the specified directory
    """
    # Load documents from the processed_txt directory for UnleashX content
    processed_txt_dir = os.path.join(data_dir, "processed_txt")
    if os.path.exists(processed_txt_dir):
        processed_loader = DirectoryLoader(processed_txt_dir, glob="**/*.txt", loader_cls=TextLoader)
        documents = processed_loader.load()
        print(f"Loaded {len(documents)} processed text documents from {processed_txt_dir}")
    else:
        documents = []
    
    # Load other text files from the data directory that aren't in processed_txt
    for root, dirs, files in os.walk(data_dir):
        # Skip the processed_txt directory since we already loaded it
        if "processed_txt" in root:
            continue
            
        txt_files = [f for f in files if f.endswith('.txt')]
        for txt_file in txt_files:
            file_path = os.path.join(root, txt_file)
            try:
                loader = TextLoader(file_path)
                file_docs = loader.load()
                documents.extend(file_docs)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
    
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