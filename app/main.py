from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from app.agents.mcp import MasterControlProgram
from app.utils.vectorstore import create_vectorstore, load_vectorstore
import uvicorn
import os
from config import API_HOST, API_PORT, APP_VERSION

# Initialize FastAPI app
app = FastAPI(
    title="General-Purpose RAG Bot",
    description="A multi-agent RAG system for answering general knowledge questions",
    version=APP_VERSION
)

# Initialize templates
templates = Jinja2Templates(directory="app/templates")

# Initialize MCP
mcp = MasterControlProgram()

# Request and response models
class QueryRequest(BaseModel):
    query: str
    agent: str = None  # Optional specific agent to use

class QueryResponse(BaseModel):
    agent: str
    response: str

class ReviewResponse(BaseModel):
    primary_agent: str
    response: str
    validation: str

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Routes
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Render the main chat interface."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/query", response_model=QueryResponse)
async def query(query_request: QueryRequest):
    """Process a query using the appropriate agent."""
    try:
        # Print the query for debugging
        print(f"\nProcessing query: {query_request.query}")
        print(f"Agent specified: {query_request.agent if query_request.agent else 'None (will be auto-selected)'}")
        
        # Process the query
        result = mcp.process_query(query_request.query, query_request.agent)
        
        # Print the response for debugging
        print(f"Response from {result['agent']} agent: {result['response'][:100]}..." if len(result['response']) > 100 else f"Response from {result['agent']} agent: {result['response']}")
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/review", response_model=ReviewResponse)
async def review(query_request: QueryRequest):
    """Process a query with validation by the tester agent."""
    try:
        result = mcp.process_with_review(query_request.query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/initialize")
async def initialize_vectorstore():
    """Initialize or reinitialize the vectorstore."""
    try:
        vectorstore = create_vectorstore()
        return {"status": "success", "message": "Vectorstore initialized successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "ok", "version": APP_VERSION}

if __name__ == "__main__":
    # Check if vectorstore exists, if not create it
    if not os.path.exists(os.path.join("vectorstore", "faiss_index")):
        print("Initializing vectorstore...")
        create_vectorstore()
    else:
        print("Vectorstore already exists. Loading...")
        load_vectorstore()
    
    # Run the API server
    uvicorn.run("app.main:app", host=API_HOST, port=API_PORT, reload=True) 