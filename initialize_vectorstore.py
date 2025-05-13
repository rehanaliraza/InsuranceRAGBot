from app.utils.vectorstore import create_vectorstore

if __name__ == "__main__":
    print("Initializing vectorstore...")
    vectorstore = create_vectorstore()
    print("Vectorstore initialization complete.") 