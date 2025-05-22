# Insurance RAG Bot

A multi-agent RAG (Retrieval-Augmented Generation) system for answering insurance-related questions.

## Features

- **Multi-Agent System**: Specialized agents for different types of insurance queries
  - Developer Agent: Technical insurance details
  - Writer Agent: Clear explanations
  - Tester Agent: Fact-checking
  - Sales Agent: Personalized product recommendations
- **Master Control Program (MCP)**: Coordinates the agents
- **Vector Database**: Uses FAISS for efficient similarity search
- **Web Interface**: Simple chat UI
- **Model-Context-Protocol Architecture**: Clean separation of concerns for better maintainability
- **Sales Intelligence**: Identifies sales opportunities and provides personalized recommendations
- **Conversational Sales Approach**: All agents are trained to include follow-up questions that identify insurance needs
- **Custom Functions**: Built-in functions that can be invoked during conversations to perform calculations or API calls

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

### With Metrics Dashboard (Recommended for development)
1. Run the application with the metrics dashboard:
   ```
   # On macOS/Linux:
   ./run_with_dashboard.sh
   
   # On Windows:
   python run_with_dashboard.py
   ```

2. This will start:
   - The main application at `http://localhost:8000`
   - The metrics dashboard at `http://localhost:8501`

3. Press `Ctrl+C` in the terminal to stop both applications

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

## Custom Functions

The InsuranceRAGBot includes a system for defining and executing custom functions during chat interactions. These functions can perform calculations, API calls, data processing, or any other operations not built into the language model.

### How Custom Functions Work

1. When a user query mentions a function call pattern like `functionName(arg1, arg2)`, the bot automatically:
   - Detects the function call in the text
   - Looks up the function in the registered custom functions
   - Executes the function with the provided arguments
   - Includes the result in the response

2. This enables interactive features like:
   - Real-time calculations
   - API calls to external services
   - Data transformations and processing
   - Insurance-specific operations

### Available Custom Functions

The bot comes with several pre-defined functions:

- `premOp(a, b)`: Adds a plus twice b
- `factorial(n)`: Calculates the factorial of a number
- `get_weather(city)`: Gets weather information for a city
- `translate_text(text, target_language)`: Translates text to another language
- `calculate_mortgage(principal, interest_rate, years)`: Calculates mortgage payments
- `extract_numbers(text)`: Extracts all numbers from a text string
- `latin_api()`: Fetches sample data from a public API

### Adding Your Own Custom Functions

To add a new custom function to the bot:

1. **Define your function in `app/utils/custom_functions.py`**

   ```python
   def my_custom_function(param1: type, param2: type) -> return_type:
       """
       Brief description of what the function does
       
       Args:
           param1: Description of first parameter
           param2: Description of second parameter
           
       Returns:
           Description of return value
           
       Example:
           my_custom_function(value1, value2) -> expected_result
       """
       logger.info(f"Executing my_custom_function({param1}, {param2})")
       
       # Function implementation
       result = ...
       
       logger.info(f"my_custom_function result: {result}")
       return result
   ```

2. **Register your function in the `CUSTOM_FUNCTIONS` dictionary**

   At the bottom of `app/utils/custom_functions.py`, add your function to the CUSTOM_FUNCTIONS dictionary:

   ```python
   CUSTOM_FUNCTIONS = {
       # ... existing functions ...
       "my_custom_function": my_custom_function
   }
   ```

3. **Follow these best practices when creating functions:**

   - **Use proper type hints** for parameters and return values
   - **Write comprehensive docstrings** with Args, Returns, and Example sections
   - **Add appropriate logging** using the logger object
   - **Include error handling** to prevent crashes
   - **Keep functions simple** and focused on a single task
   - **Validate input parameters** to prevent unexpected behavior
   - **Format return values** consistently

4. **Test your function**

   Use the provided test scripts to verify your function works correctly:

   ```bash
   # Basic test script
   python test_custom_functions.py
   
   # Interactive testing tool
   python custom_function_test.py
   ```

   The interactive testing tool allows you to:
   - Test functions directly with custom arguments
   - Test function detection in various text formats
   - Simulate how the bot processes function calls in responses

### Function Execution Process

When the bot detects a potential function call in text:

1. It extracts the function name and arguments using regex pattern matching
2. Arguments are parsed and converted to appropriate types (numbers, strings, booleans)
3. The function is executed with the provided arguments
4. The result is formatted and inserted back into the response
5. A record of the function call is maintained for logging and metrics

### Advanced Function Features

The custom function system includes several advanced features:

- **Deduplication**: If the same function with the same arguments is called multiple times, it's only executed once
- **Error Handling**: If a function throws an exception, the error is captured and displayed in the response
- **Type Conversion**: Arguments are automatically converted to appropriate types (strings, numbers, booleans)
- **Result Formatting**: Complex results (like dictionaries or lists) are properly formatted as JSON
- **Function Descriptions**: Get descriptions of all available functions with `get_function_descriptions()`

### Example Usage

Users can trigger custom functions by simply mentioning them in their queries:

- "What would my mortgage payment be for calculate_mortgage(300000, 0.035, 30)?"
- "I need to know factorial(5) for my calculation."
- "What's the weather like in get_weather('New York')?"

The bot will automatically execute these functions and include the results in its response.

## Adding Custom Documents

1. Place your insurance document text files in the `app/data` directory
2. The system will automatically process and index these documents when it starts
3. To manually reindex documents:
   ```
   # Use the API endpoint
   curl -X POST http://localhost:8000/api/initialize
   
   # Or restart the application
   ```

4. For sales materials, place documents in the `app/data/sales` directory

### PDF, Excel, and CSV Support

The system now supports converting PDF, Excel (XLSX), and CSV files to text format:

1. Use the document helper tool:
   ```
   # Convert a document
   ./document_helper.py convert path/to/your/document.pdf
   
   # List all documents in the system
   ./document_helper.py list
   
   # Reinitialize the vectorstore
   ./document_helper.py initialize
   ```

2. Or use the API endpoint directly:
   ```
   # Convert a document via API
   curl -X POST http://localhost:8000/api/convert-document \
     -H "Content-Type: application/json" \
     -d '{"file_path": "path/to/your/document.pdf"}'
   
   # Then initialize the vectorstore
   curl -X POST http://localhost:8000/api/initialize
   ```

The conversion process automatically:
- Extracts text from the document
- Cleans and filters content to focus on insurance-relevant information
- Saves the processed text in the app/data directory
- Updates the vectorstore with the new content

## Knowledge Base Management

The knowledge base is the foundation of the RAG system, containing all documents used for answering queries.

### What is the Knowledge Base?

The knowledge base consists of:
1. **Text Documents**: Stored in the `app/data` directory
2. **Vector Embeddings**: Generated from these documents and stored in the `vectorstore` directory
3. **Retrieval System**: The mechanism that finds relevant information based on user queries

### Adding New Documents to the Knowledge Base

There are three ways to add new documents:

#### Method 1: Using the document_helper.py tool (Recommended)

1. Ensure the document_helper.py is executable:
   ```
   chmod +x document_helper.py
   ```

2. Run the conversion command:
   ```
   ./document_helper.py convert /path/to/your/document.pdf
   ```
   
3. The tool will:
   - Extract and clean the document content
   - Save it as a text file in app/data
   - Automatically update the vectorstore

#### Method 2: Using the API

1. Start the server if not already running:
   ```
   python run_mcp.py
   ```

2. Send a POST request to convert the document:
   ```
   curl -X POST http://localhost:8000/api/convert-document \
     -H "Content-Type: application/json" \
     -d '{"file_path": "/path/to/your/document.pdf"}'
   ```

#### Method 3: Manual Addition

1. Create or place a text file in the `app/data` directory
2. Run the initialization script to update the vectorstore:
   ```
   python init_vectorstore.py
   ```
   
   Or use the API endpoint:
   ```
   curl -X POST http://localhost:8000/api/initialize
   ```

### Supported File Types

- **PDF Documents** (.pdf)
- **Excel Spreadsheets** (.xlsx, .xls)
- **CSV Files** (.csv)
- **Plain Text Files** (.txt)

### Verifying Document Addition

To verify your document was added to the knowledge base:

1. List all documents in the system:
   ```
   ./document_helper.py list
   ```

2. Test the bot with a question related to the new document content
   ```
   curl -X POST http://localhost:8000/api/query \
     -H "Content-Type: application/json" \
     -d '{"query": "Tell me about [topic from your new document]"}'
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
    - `sales/`: Sales materials and scenarios
  - `templates/`: HTML templates
  - `static/`: CSS and other static files
  - `utils/`: Utility functions
    - `custom_functions.py`: Custom functions for the bot
    - `function_parser.py`: Parser for detecting and executing functions
  - `main.py`: Original FastAPI application
  - `main_mcp.py`: MCP-based FastAPI application
- `config.py`: Configuration settings
- `requirements.txt`: Dependencies
- `start.py`: Full system launcher script (original architecture)
- `run_mcp.py`: MCP architecture launcher script
- `simple_app.py`: Simplified version for easier startup
- `fix_imports.py`: Helper script to fix LangChain imports
- `test_openai.py`: Test script for OpenAI API connectivity
- `test_custom_functions.py`: Test script for custom functions
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

## Insurance Sales Agent

The Insurance Sales Agent extends the system's capabilities to provide personalized product recommendations:

### Features

- **Consultative Approach**: Provides helpful information first, then identifies sales opportunities
- **Situation Analysis**: Identifies aspects of the user's situation that indicate specific insurance needs
- **Follow-up Questions**: Asks relevant questions to better understand the user's situation
- **Product Recommendations**: Suggests appropriate insurance products based on identified needs
- **Conversation Transitions**: Smoothly transitions from information to sales exploration

### Sales-Driven Conversation Flow

The system uses multiple techniques to drive insurance sales opportunities:

1. **Universal Follow-up Questions**: Every agent (not just the Sales Agent) is trained to include natural follow-up questions that uncover insurance needs 
2. **Intelligent Agent Routing**: The system analyzes conversations to identify when to transition to the Sales Agent
3. **Sales Keyword Detection**: Automatically routes queries with sales-related keywords to the Sales Agent
4. **Conversation Context Analysis**: Monitors conversation history to identify signals of sales readiness
5. **Response Post-Processing**: Ensures all responses end with an appropriate follow-up question if one isn't already included
6. **Progressive Engagement**: After multiple exchanges, increasingly transitions to sales-oriented interactions

### Sales Materials

The system includes specialized sales materials:

- **Product Information**: Detailed descriptions of various insurance products
- **Customer Scenarios**: Common situations and appropriate product recommendations
- **Conversation Templates**: Examples of effective transitions from information to sales
- **Objection Handling**: Strategies for addressing common customer concerns

To add new sales materials, place text files in the `app/data/sales` directory.

## License

[MIT License](LICENSE)

## Metrics Dashboard

The InsuranceRAGBot includes a Streamlit-based metrics dashboard for monitoring system performance:

### Features

- **Real-time Metrics**: Monitor latency, token usage, agent distribution, and retrieval performance
- **Filtering**: Filter data by date range and agent type
- **Data Visualization**: Interactive charts for metrics analysis
- **Auto-refresh**: Option to automatically refresh the dashboard
- **Time-series Analysis**: View metrics trends over time

### Tracked Metrics

- **Latency**: Response times for different operations (routing, retrieval, LLM generation, etc.)
- **Token Usage**: Prompt and completion token usage by agent type and model
- **Agent Distribution**: Frequency of agent type usage
- **Retrieval Metrics**: Number of documents retrieved and performance
- **Query Types**: Distribution of different query types (routed, direct, etc.)

### Running the Dashboard

To run the metrics dashboard:

```
# Make sure your virtual environment is activated
streamlit run dashboard.py
```

Then open your browser and navigate to the URL displayed in the terminal (usually `http://localhost:8501`).

### Dashboard Components

1. **System Overview**: Key performance indicators like average response time and total tokens used
2. **Latency Analysis**: Charts showing response times over time for different operations
3. **Agent Usage Analysis**: Distribution of agent types and query types
4. **Token Usage Analysis**: Token consumption by agent type and token type (prompt vs. completion)
5. **Retrieval Metrics**: Document retrieval statistics and effectiveness

### Managing Metrics Data

The dashboard runs independently from the main application, allowing you to monitor metrics without affecting the bot's performance.

Several utilities are available for managing metrics data:

1. **Cleaning Metrics**: To remove test/fabricated data while preserving real metrics:
   ```
   python3 clean_metrics.py
   ```

2. **Resetting Metrics**: To completely reset all metrics data (with backup):
   ```
   python3 reset_metrics.py
   ```

3. **Generating Test Data**: If you need sample data to test the dashboard:
   ```
   python3 generate_test_metrics.py
   ```

Metrics are automatically collected during normal operation of the bot. The more queries you process through the bot, the more comprehensive the metrics visualizations will become.

## TryUnleashX Integration

The InsuranceRAGBot includes integration with the TryUnleashX platform for knowledge management:

### Features

- **Knowledge Sync**: Automatically fetch and incorporate knowledge from TryUnleashX
- **Multiple Content Types**: Support for files (PDF, XLSX, CSV), web links, and HTML pages
- **Content Processing**: Intelligent extraction and filtering of insurance-relevant content
- **Command-Line Tool**: Dedicated tool for syncing knowledge from TryUnleashX

### Using the Integration

1. **API Endpoint**: Use the `/api/sync-unleashx` endpoint to sync knowledge from TryUnleashX
   ```
   POST /api/sync-unleashx
   {
     "token": "your-unleashx-api-token",
     "agent_id": 123
   }
   ```

2. **Command-Line Tool**: Use the `sync_unleashx.py` script for direct syncing
   ```
   python sync_unleashx.py --agent_id 123 --token your-unleashx-api-token
   ```

For detailed documentation, see [UNLEASHX_SYNC_README.md](UNLEASHX_SYNC_README.md).