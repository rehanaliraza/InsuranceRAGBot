"""
Insurance RAG Bot - Main application using MCP architecture
"""
import os
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn
from app.mcp.executor import MCPExecutor
from app.utils.vectorstore import create_vectorstore, load_vectorstore
from app.utils.document_converter import save_as_text_file
from config import API_HOST, API_PORT, APP_VERSION

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("main_mcp")

# Initialize FastAPI app
app = FastAPI(
    title="Insurance RAG Bot (MCP)",
    description="A multi-agent RAG system using Model-Context-Protocol architecture",
    version=APP_VERSION
)

# Initialize templates
templates = Jinja2Templates(directory="app/templates")

# Initialize MCP Executor
mcp_executor = MCPExecutor()

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

class DocumentConversionRequest(BaseModel):
    file_path: str  # Path to the document file

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Routes
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Render the main chat interface."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/query", response_model=QueryResponse)
async def query(query_request: QueryRequest):
    """Process a query using the MCP executor."""
    try:
        logger.info(f"Received query: {query_request.query}")
        
        # Execute query using MCP executor
        result = mcp_executor.execute_query(
            query=query_request.query, 
            agent_type=query_request.agent
        )
        
        # Format the agent name for display in the UI
        if result['agent'] == 'system':
            # For system responses (like history queries), use a special agent name
            display_agent = 'System'
        else:
            # For regular agent responses, format nicely for display
            display_agent = result['agent'].capitalize()
            
        logger.info(f"Query processed successfully by {result['agent']}")
        
        # Return the properly formatted result
        return {
            "agent": display_agent,
            "response": result['response']
        }
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/sales", response_model=QueryResponse)
async def sales_query(query_request: QueryRequest):
    """Process a query specifically using the Sales Agent."""
    try:
        logger.info(f"Received sales query: {query_request.query}")
        
        # Force the sales agent to be used
        result = mcp_executor.execute_query(
            query=query_request.query,
            agent_type="sales"
        )
        
        logger.info(f"Sales query processed successfully")
        return {
            "agent": "Sales",
            "response": result['response']
        }
    except Exception as e:
        logger.error(f"Error processing sales query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/review", response_model=ReviewResponse)
async def review(query_request: QueryRequest):
    """Process a query with validation by the tester agent."""
    try:
        logger.info(f"Received review request: {query_request.query}")
        
        # Execute query with review using MCP executor
        result = mcp_executor.execute_with_review(query_request.query)
        
        logger.info(f"Review processed successfully by {result['primary_agent']}")
        return result
    except Exception as e:
        logger.error(f"Error processing review: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/initialize")
async def initialize_vectorstore():
    """Initialize or reinitialize the vectorstore."""
    try:
        logger.info("Initializing vectorstore")
        vectorstore = create_vectorstore()
        # Reset the context manager's vectorstore
        mcp_executor.context_manager._vectorstore = vectorstore
        return {"status": "success", "message": "Vectorstore initialized successfully"}
    except Exception as e:
        logger.error(f"Error initializing vectorstore: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/convert-document")
async def convert_document(conversion_request: DocumentConversionRequest):
    """Convert a document (PDF, XLSX, CSV) to cleaned text and save it."""
    try:
        logger.info(f"Converting document: {conversion_request.file_path}")
        
        # Validate file exists
        if not os.path.isfile(conversion_request.file_path):
            raise HTTPException(status_code=404, detail=f"File not found: {conversion_request.file_path}")
            
        # Get file extension
        _, ext = os.path.splitext(conversion_request.file_path)
        ext = ext.lower()
        
        # Check supported formats
        supported_formats = ['.pdf', '.xlsx', '.xls', '.csv']
        if ext not in supported_formats:
            raise HTTPException(status_code=400, detail=f"Unsupported file format: {ext}. Supported formats are {', '.join(supported_formats)}")
        
        # Use data directory for output
        output_dir = "app/data"
        
        # Convert document to text
        text_path = save_as_text_file(conversion_request.file_path, output_dir)
        
        if text_path:
            return {
                "status": "success", 
                "message": "Document converted successfully", 
                "text_path": text_path
            }
        else:
            raise HTTPException(status_code=500, detail=f"Failed to convert document")
            
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise e
    except Exception as e:
        logger.error(f"Error converting document: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "ok", "version": APP_VERSION, "architecture": "MCP"}

if __name__ == "__main__":
    # Check if vectorstore exists, if not create it
    if not os.path.exists(os.path.join("vectorstore", "faiss_index")):
        logger.info("Initializing vectorstore...")
        create_vectorstore()
    else:
        logger.info("Vectorstore already exists. Loading...")
        load_vectorstore()
    
    # Run the API server
    uvicorn.run("app.main_mcp:app", host=API_HOST, port=API_PORT, reload=True) 