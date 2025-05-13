#!/usr/bin/env python3
"""
Simplified version of the Insurance RAG Bot that focuses on just loading documents
and providing basic API functionality without agent complexity
"""
import os
import sys
import traceback

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn
from config import API_HOST, API_PORT, APP_VERSION

# Initialize FastAPI app
app = FastAPI(
    title="Insurance RAG Bot (Simple)",
    description="A simplified RAG system for insurance questions",
    version=APP_VERSION
)

# Mount static files
os.makedirs("app/static", exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Initialize templates
os.makedirs("app/templates", exist_ok=True)
templates = Jinja2Templates(directory="app/templates")

# Request and response models
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    response: str
    source: str

# Setup the vectorstore
os.makedirs("vectorstore", exist_ok=True)
vectorstore = None

def init_vectorstore():
    """Initialize the vectorstore if needed"""
    global vectorstore
    if vectorstore is None:
        try:
            from app.utils.vectorstore import load_vectorstore
            vectorstore = load_vectorstore()
            print("Vectorstore loaded successfully")
        except Exception as e:
            print(f"Error loading vectorstore: {e}")
            traceback.print_exc()
            return False
    return True

# Routes
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Render the main chat interface."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "ok", "version": APP_VERSION}

@app.post("/api/query", response_model=QueryResponse)
async def query(query_request: QueryRequest):
    """Process a simple query against the vectorstore"""
    if not init_vectorstore():
        raise HTTPException(status_code=500, detail="Vectorstore not available")
    
    try:
        from app.utils.vectorstore import get_relevant_documents
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        from config import OPENAI_API_KEY
        
        # Get relevant documents
        docs = get_relevant_documents(query_request.query, vectorstore)
        context = "\n\n".join(doc.page_content for doc in docs)
        
        # Format source for citation
        source = docs[0].metadata.get("source", "unknown") if docs else "No relevant documents found"
        
        # Create prompt
        prompt = ChatPromptTemplate.from_template("""
        You are an insurance assistant. Use the following context to answer the question.
        
        Context:
        {context}
        
        Question: {question}
        
        Answer:
        """)
        
        # Create LLM
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.2,
            openai_api_key=OPENAI_API_KEY
        )
        
        # Create chain
        chain = prompt | llm | StrOutputParser()
        
        # Run chain
        response = chain.invoke({"context": context, "question": query_request.query})
        
        return {"response": response, "source": source}
    except Exception as e:
        print(f"Error processing query: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/initialize")
async def initialize_vectorstore():
    """Initialize or reinitialize the vectorstore."""
    global vectorstore
    try:
        from app.utils.vectorstore import create_vectorstore
        vectorstore = create_vectorstore()
        return {"status": "success", "message": "Vectorstore initialized successfully"}
    except Exception as e:
        print(f"Error initializing vectorstore: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

def main():
    # Initialize vectorstore
    if not init_vectorstore():
        print("Warning: Vectorstore initialization failed. API calls may fail.")
    
    # Start the server
    uvicorn.run(app, host=API_HOST, port=API_PORT)

if __name__ == "__main__":
    main() 