import os
from dotenv import load_dotenv

# App version
APP_VERSION = "0.1.0"

# Load environment variables
load_dotenv()

# OpenAI API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Vector Database Configuration
VECTOR_DB_PATH = "vectorstore"

# Chunking Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Agent Configuration
AGENTS = {
    "developer": {
        "name": "Developer Agent",
        "description": "Specializes in technical concepts and detailed explanations",
        "temperature": 0.2
    },
    "writer": {
        "name": "Writer Agent",
        "description": "Specializes in clear, concise explanations of complex concepts",
        "temperature": 0.5
    },
    "tester": {
        "name": "Tester Agent",
        "description": "Validates answers for factual accuracy and correctness",
        "temperature": 0.0
    }
}

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 8000 