# Insurance RAG Bot

A multi-agent RAG (Retrieval-Augmented Generation) system for answering insurance-related questions.

## Features

- **Multi-Agent System**: Specialized agents for different types of insurance queries
  - Developer Agent: Technical insurance details
  - Writer Agent: Clear explanations
  - Tester Agent: Fact-checking
- **Master Control Program (MCP)**: Coordinates the agents
- **Vector Database**: Uses FAISS for efficient similarity search
- **Web Interface**: Simple chat UI

## Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd InsuranceRAGBot
   ```

2. Create a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Edit the `.env` file in the root directory
   - Add your OpenAI API key: `OPENAI_API_KEY=your_key_here`

## Usage

### Basic Usage (Recommended for first run)
1. Run the simplified app:
   ```
   # Make sure your virtual environment is activated
   python3 simple_app.py
   ```

2. Open your browser and navigate to `http://localhost:8000`

### Full Multi-Agent System
1. Run the full application:
   ```
   python3 start.py
   ```

## Troubleshooting

If you encounter issues:

1. **OpenAI API Key**: Make sure your OpenAI API key is correctly set in the `.env` file
   ```
   # Test your API key with
   python3 test_openai.py
   ```

2. **Import Issues**: If you see deprecation warnings, run the fix_imports script:
   ```
   python3 fix_imports.py
   ```

3. **Vectorstore Problems**: If the vectorstore fails to initialize, try running:
   ```
   python3 init_vectorstore.py
   ```

4. **Python Version**: Ensure you're using Python 3.9+ (`python3 --version`)

5. **Package Issues**: Make sure all dependencies are installed:
   ```
   pip install -r requirements.txt
   ```

## Adding Custom Documents

1. Place your insurance document text files in the `app/data` directory
2. The system will automatically process and index these documents when it starts
3. To manually reindex documents:
   ```
   # Use the API endpoint
   curl -X POST http://localhost:8000/api/initialize
   
   # Or restart the application
   ```

## Project Structure

- `app/`: Main application code
  - `agents/`: Agent implementations
  - `data/`: Insurance document files
  - `templates/`: HTML templates
  - `static/`: CSS and other static files
  - `utils/`: Utility functions
  - `main.py`: FastAPI application
- `config.py`: Configuration settings
- `requirements.txt`: Dependencies
- `start.py`: Full system launcher script
- `simple_app.py`: Simplified version for easier startup
- `fix_imports.py`: Helper script to fix LangChain imports
- `test_openai.py`: Test script for OpenAI API connectivity
- `init_vectorstore.py`: Script to initialize the vectorstore

## License

[MIT License](LICENSE) 