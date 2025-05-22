"""
Test script to verify custom function execution in the InsuranceRAGBot
"""
import sys
import os
import logging

# Add the project root to Python path to ensure imports work
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Configure logging to see all messages
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Import custom functions and function parser
from app.utils.custom_functions import execute_function, CUSTOM_FUNCTIONS, get_function_descriptions
from app.utils.function_parser import FunctionDetectionParser
from app.mcp.executor import MCPExecutor

def test_function_execution():
    """Test direct execution of custom functions"""
    print("\n=== TESTING DIRECT FUNCTION EXECUTION ===")
    
    # Test a few functions directly
    try:
        # Test premOp function
        result = execute_function("premOp", [5, 3])
        print(f"premOp(5, 3) = {result}")
        
        # Test yatiOp function
        result = execute_function("yatiOp", [7])
        print(f"yatiOp(7) = {result}")
        
        # Test factorial function
        result = execute_function("factorial", [5])
        print(f"factorial(5) = {result}")
        
        # Test weather function
        result = execute_function("get_weather", ["London"])
        print(f"get_weather('London') = {result}")
        
    except Exception as e:
        print(f"Error in direct function execution: {e}")

def test_function_detection():
    """Test detection and execution of functions in text"""
    print("\n=== TESTING FUNCTION DETECTION IN TEXT ===")
    
    # Create a function parser
    parser = FunctionDetectionParser()
    
    # Test texts containing function calls
    test_texts = [
        "To calculate this, we use premOp(5, 3) which gives us the answer.",
        "The factorial of 5 is factorial(5).",
        "London weather: get_weather('London')",
        "For mortgage calculation, we use calculate_mortgage(200000, 0.045, 30).",
        "Let me translate 'hello' to Spanish: translate_text('hello', 'es')",
        "Complex text with multiple functions: premOp(2, 3) and factorial(4) and yatiOp(5)"
    ]
    
    for text in test_texts:
        print(f"\nOriginal text: {text}")
        processed_text, function_calls = parser.detect_and_execute_functions(text)
        print(f"Processed text: {processed_text}")
        
        if function_calls:
            print("Functions detected and executed:")
            for call in function_calls:
                print(f"  - {call['function']}({', '.join(map(str, call['arguments']))}) = {call['result']}")
        else:
            print("No functions detected in this text")

def test_with_function_parser():
    """Test the main parse method of the function parser"""
    print("\n=== TESTING FUNCTION PARSER ===")
    
    parser = FunctionDetectionParser()
    
    test_responses = [
        """
        The result of premOp(5, 3) is calculated by adding 5 plus twice 3.
        
        You can also calculate the factorial of a number using factorial(5).
        """,
        
        """
        Let me tell you about the weather in London:
        get_weather('London')
        
        For your mortgage question, calculate_mortgage(200000, 0.045, 30) provides the monthly payment.
        """
    ]
    
    for response in test_responses:
        print(f"\nOriginal response:\n{response}")
        processed = parser.parse(response)
        print(f"Processed response:\n{processed}")
        
        # Get and display function calls
        function_calls = parser.get_function_calls()
        if function_calls:
            print("\nFunctions executed:")
            for call in function_calls:
                print(f"  - {call['function']}({', '.join(map(str, call['arguments']))}) = {call['result']}")
        else:
            print("\nNo functions executed")

def test_mcp_executor():
    """Test function execution through the MCP executor"""
    print("\n=== TESTING MCP EXECUTOR ===")
    
    # Print available functions
    print("Available functions:")
    for name, desc in get_function_descriptions().items():
        print(f"  - {name}: {desc}")
    
    # Initialize MCP executor
    executor = MCPExecutor()
    
    # Test queries that should trigger function execution
    test_queries = [
        "What is premOp(4, 2)?",
        "Calculate factorial(5) for me",
        "What is the weather in London? Use get_weather('London')",
        "Tell me about mortgage payments using calculate_mortgage(250000, 0.04, 30)",
        "Translate 'hello' to Spanish using translate_text('hello', 'es')"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        
        # Execute the query
        result = executor.execute_query(query)
        
        # Print the response
        agent_type = result.get("agent", "unknown")
        response = result.get("response", "No response")
        
        print(f"Agent: {agent_type}")
        print(f"Response: {response[:200]}..." if len(response) > 200 else f"Response: {response}")
        
        # Print any metrics about function calls
        metrics = result.get("metrics", {})
        if "functions_called" in metrics:
            print("Functions called:")
            for func in metrics["functions_called"]:
                print(f"  - {func['name']}({', '.join(map(str, func['args']))})")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("TESTING CUSTOM FUNCTIONS")
    print("="*80)
    
    # Test direct function execution
    test_function_execution()
    
    # Test function detection
    test_function_detection()
    
    # Test with function parser
    test_with_function_parser()
    
    # Test with MCP executor
    test_mcp_executor()
    
    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80)

# Configure logging to see all messages
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Import custom functions and function parser
from app.utils.custom_functions import execute_function, CUSTOM_FUNCTIONS
from app.utils.function_parser import FunctionDetectionParser

def test_function_execution():
    """Test direct execution of custom functions"""
    print("\n=== TESTING DIRECT FUNCTION EXECUTION ===")
    
    # Test a few functions directly
    try:
        # Test premOp function
        result = execute_function("premOp", [5, 3])
        print(f"premOp(5, 3) = {result}")
        
        # Test yatiOp function
        result = execute_function("yatiOp", [7])
        print(f"yatiOp(7) = {result}")
        
        # Test factorial function
        result = execute_function("factorial", [5])
        print(f"factorial(5) = {result}")
        
        # Test weather function
        result = execute_function("get_weather", ["London"])
        print(f"get_weather('London') = {result}")
        
    except Exception as e:
        print(f"Error in direct function execution: {e}")

def test_function_detection():
    """Test detection and execution of functions in text"""
    print("\n=== TESTING FUNCTION DETECTION IN TEXT ===")
    
    # Create a function parser
    parser = FunctionDetectionParser()
    
    # Test texts containing function calls
    test_texts = [
        "To calculate this, we use premOp(5, 3) which gives us the answer.",
        "The factorial of 5 is factorial(5).",
        "London weather: get_weather('London')",
        "For mortgage calculation, we use calculate_mortgage(200000, 0.045, 30).",
        "Let me translate 'hello' to Spanish: translate_text('hello', 'es')",
        "Complex text with multiple functions: premOp(2, 3) and factorial(4) and yatiOp(5)"
    ]
    
    for text in test_texts:
        print(f"\nOriginal text: {text}")
        processed_text, function_calls = parser.detect_and_execute_functions(text)
        print(f"Processed text: {processed_text}")
        
        if function_calls:
            print("Functions detected and executed:")
            for call in function_calls:
                print(f"  - {call['function']}({', '.join(map(str, call['arguments']))}) = {call['result']}")
        else:
            print("No functions detected in this text")

def test_with_function_parser():
    """Test the main parse method of the function parser"""
    print("\n=== TESTING FUNCTION PARSER ===")
    
    parser = FunctionDetectionParser()
    
    test_responses = [
        """
        The result of premOp(5, 3) is calculated by adding 5 plus twice 3.
        
        You can also calculate the factorial of a number using factorial(5).
        """,
        
        """
        Let me tell you about the weather in London:
        get_weather('London')
        
        For your mortgage question, calculate_mortgage(200000, 0.045, 30) provides the monthly payment.
        """
    ]
    
    for response in test_responses:
        print(f"\nOriginal response:\n{response}")
        processed = parser.parse(response)
        print(f"Processed response:\n{processed}")
        
        # Get and display function calls
        function_calls = parser.get_function_calls()
        if function_calls:
            print("\nFunctions executed:")
            for call in function_calls:
                print(f"  - {call['function']}({', '.join(map(str, call['arguments']))}) = {call['result']}")
        else:
            print("\nNo functions executed")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("TESTING CUSTOM FUNCTIONS")
    print("="*80)
    
    # Test direct function execution
    test_function_execution()
    
    # Test function detection
    test_function_detection()
    
    # Test with function parser
    test_with_function_parser()
    
    print("\n" + "="*80)
    print("TESTING COMPLETE")
    print("="*80)
