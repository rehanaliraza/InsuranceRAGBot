"""
Custom Function Test - Interactive Testing Tool for InsuranceRAGBot Custom Functions

This script allows you to test custom functions directly and through the bot's function parser system.
Use this to verify that your custom functions are working correctly before deploying them.

Usage:
1. Run the script: python custom_function_test.py
2. Follow the interactive prompts to:
   - Test individual functions directly
   - Test function detection in text
   - Test the bot's response to function calls
"""
import sys
import os
import logging
from typing import Any, Dict, List

# Add the project root to Python path to ensure imports work
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Configure logging to see all messages
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Import custom functions and function parser
from app.utils.custom_functions import execute_function, CUSTOM_FUNCTIONS, get_function_descriptions
from app.utils.function_parser import FunctionDetectionParser

class InteractiveFunctionTester:
    """Interactive console for testing custom functions"""
    
    def __init__(self):
        self.functions = CUSTOM_FUNCTIONS
        self.parser = FunctionDetectionParser()
        
    def display_menu(self):
        """Display the main menu options"""
        print("\n" + "="*80)
        print(" CUSTOM FUNCTION TESTER".center(80))
        print("="*80)
        print("\nAvailable functions:")
        
        for name, func in self.functions.items():
            doc = func.__doc__.split('\n')[0].strip() if func.__doc__ else "No description"
            print(f"  - {name}: {doc}")
        
        print("\nOptions:")
        print("  1. Test a function directly")
        print("  2. Test function detection in text")
        print("  3. Simulate bot response with functions")
        print("  4. Exit")
        
        choice = input("\nEnter your choice (1-4): ")
        return choice
        
    def test_function_directly(self):
        """Interactive test of direct function execution"""
        print("\n" + "-"*80)
        print(" TEST FUNCTION DIRECTLY ".center(80))
        print("-"*80)
        
        # Get function name
        while True:
            func_name = input("\nEnter function name (or 'list' to see available functions): ")
            
            if func_name.lower() == 'list':
                for name in self.functions.keys():
                    print(f"  - {name}")
                continue
                
            if func_name in self.functions:
                break
            else:
                print(f"Function '{func_name}' not found. Try again.")
        
        # Get function arguments
        function = self.functions[func_name]
        print(f"\nFunction: {func_name}")
        if function.__doc__:
            print(f"Description: {function.__doc__.strip()}")
            
        args = []
        while True:
            arg_input = input("\nEnter argument (or 'done' when finished): ")
            if arg_input.lower() == 'done':
                break
                
            # Try to convert to appropriate type
            try:
                # Try as number first
                if '.' in arg_input:
                    args.append(float(arg_input))
                else:
                    args.append(int(arg_input))
            except ValueError:
                # Then as boolean
                if arg_input.lower() == 'true':
                    args.append(True)
                elif arg_input.lower() == 'false':
                    args.append(False)
                elif arg_input.lower() in ('none', 'null'):
                    args.append(None)
                else:
                    # Otherwise as string (remove quotes if present)
                    if (arg_input.startswith('"') and arg_input.endswith('"')) or \
                       (arg_input.startswith("'") and arg_input.endswith("'")):
                        args.append(arg_input[1:-1])
                    else:
                        args.append(arg_input)
            
            print(f"Added argument: {args[-1]} (type: {type(args[-1]).__name__})")
        
        # Execute function
        print("\nExecuting function...")
        try:
            result = execute_function(func_name, args)
            print(f"\nResult: {result}")
            print(f"Result type: {type(result).__name__}")
        except Exception as e:
            print(f"\nError executing function: {e}")
    
    def test_function_detection(self):
        """Interactive test of function detection in text"""
        print("\n" + "-"*80)
        print(" TEST FUNCTION DETECTION ".center(80))
        print("-"*80)
        
        print("\nEnter a text that contains function calls.")
        print("Example: 'The result of premOp(5, 3) is calculated as follows.'")
        
        text = input("\nEnter text: ")
        
        print("\nDetecting and executing functions...")
        processed_text, function_calls = self.parser.detect_and_execute_functions(text)
        
        print(f"\nProcessed text:\n{processed_text}")
        
        if function_calls:
            print("\nFunctions detected and executed:")
            for call in function_calls:
                args_str = ', '.join(repr(arg) for arg in call['arguments'])
                print(f"  - {call['function']}({args_str}) = {call['result']}")
        else:
            print("\nNo functions were detected in the text.")
    
    def simulate_bot_response(self):
        """Simulate a bot response with function calls"""
        print("\n" + "-"*80)
        print(" SIMULATE BOT RESPONSE ".center(80))
        print("-"*80)
        
        print("\nThis simulates how the bot processes function calls in responses.")
        print("Enter a mock bot response that might contain function calls.")
        print("Example: 'Based on your information, your monthly payment would be calculate_mortgage(200000, 0.045, 30).'")
        
        response = input("\nEnter mock bot response: ")
        
        print("\nProcessing response with the function parser...")
        processed = self.parser.parse(response)
        
        print(f"\nProcessed response:\n{processed}")
        
        # Get and display function calls
        function_calls = self.parser.get_function_calls()
        if function_calls:
            print("\nFunctions executed:")
            for call in function_calls:
                args_str = ', '.join(repr(arg) for arg in call['arguments'])
                print(f"  - {call['function']}({args_str}) = {call['result']}")
        else:
            print("\nNo functions were executed.")
    
    def run(self):
        """Run the interactive tester"""
        while True:
            choice = self.display_menu()
            
            if choice == '1':
                self.test_function_directly()
            elif choice == '2':
                self.test_function_detection()
            elif choice == '3':
                self.simulate_bot_response()
            elif choice == '4':
                print("\nExiting. Goodbye!")
                break
            else:
                print("\nInvalid choice. Please enter a number between 1 and 4.")
            
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    tester = InteractiveFunctionTester()
    tester.run()
