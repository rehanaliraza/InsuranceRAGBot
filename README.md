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
- **Model-Context-Protocol Architecture**: Clean separation of concerns for better maintainability

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

### MCP Architecture Version
1. Run the MCP-based version:
   ```
   python3 run_mcp.py
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
  - `agents/`: Original agent implementations
  - `mcp/`: Model-Context-Protocol implementation
    - `models.py`: Language model management
    - `context.py`: Context management (documents & history)
    - `protocol.py`: Prompt templates and output parsing
    - `executor.py`: Integrates models, context, and protocols
  - `data/`: Insurance document files
  - `templates/`: HTML templates
  - `static/`: CSS and other static files
  - `utils/`: Utility functions
  - `main.py`: Original FastAPI application
  - `main_mcp.py`: MCP-based FastAPI application
- `config.py`: Configuration settings
- `requirements.txt`: Dependencies
- `start.py`: Full system launcher script (original architecture)
- `run_mcp.py`: MCP architecture launcher script
- `simple_app.py`: Simplified version for easier startup
- `fix_imports.py`: Helper script to fix LangChain imports
- `test_openai.py`: Test script for OpenAI API connectivity
- `init_vectorstore.py`: Script to initialize the vectorstore

## Model-Context-Protocol (MCP) Architecture

The system includes an implementation of the Model-Context-Protocol architecture, which separates concerns into three primary components:

### 1. Model Component

The Model component manages the language models used by the system:

- **ModelProvider Class**: Acts as a factory for different language model instances
- **Different Model Configurations**: Each agent type has its own model configuration
- **Consistent Interface**: Unified way to access models regardless of their specific implementation

### 2. Context Component

The Context component manages all contextual information needed for generating responses:

- **Document Retrieval**: Gets relevant documents from the vectorstore based on query
- **Conversation History**: Tracks and formats previous interactions (stored in-memory)
- **Context Preparation**: Formats documents and history for inclusion in prompts

### 3. Protocol Component

The Protocol component standardizes how the system interacts with models:

- **PromptProtocol**: Defines specialized prompt templates for each agent type
- **OutputProtocol**: Manages how model outputs are parsed and formatted
- **AgentType Enum**: Standardizes references to different agent types

### Integration via MCPExecutor

The `MCPExecutor` class brings all three components together:

- **Query Routing**: Determines which agent type should handle a query
- **Context Collection**: Gets relevant documents and conversation history
- **Prompt Selection**: Chooses the appropriate prompt template
- **Response Validation**: Can review responses using the tester agent

### Benefits of MCP Architecture

- **Separation of Concerns**: Each component has a clear responsibility
- **Flexibility**: Easy to add new models, context sources, or prompt templates
- **Standardization**: Consistent interfaces between components
- **Extensibility**: New agent types can be added with minimal changes

## License

[MIT License](LICENSE) 