"""
Function Detection Parser - Detects and executes custom functions in bot responses

This module provides the parser that scans bot responses for function calls,
executes the functions, and integrates the results back into the response.
"""
import re
import json
import logging
from typing import Any, List, Dict, Tuple, Optional
from app.utils.custom_functions import CUSTOM_FUNCTIONS, execute_function

# Setup logging
logger = logging.getLogger("function_parser")

class FunctionDetectionParser:
    """
    Parser that detects function calls in text and executes them
    """
    def __init__(self):
        self.functions = CUSTOM_FUNCTIONS
        self.function_pattern = r'(\w+)\(([^)]*)\)'
        
        # Create a log of function calls for reporting
        self.function_calls = []
    
    def clear_function_calls(self):
        """Clear the log of function calls"""
        self.function_calls = []
    
    def get_function_calls(self) -> List[Dict[str, Any]]:
        """Get the log of function calls"""
        return self.function_calls
    
    def parse_arguments(self, args_str: str) -> List[Any]:
        """
        Parse function arguments from string format
        
        Args:
            args_str: Comma-separated arguments string
            
        Returns:
            List of parsed arguments
        """
        if not args_str.strip():
            return []
            
        # Split by comma, but respect quoted strings
        args = []
        current_arg = ""
        in_quotes = False
        quote_char = None
        
        for char in args_str:
            if char in ['"', "'"]:
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                elif char == quote_char:
                    in_quotes = False
                    quote_char = None
                current_arg += char
            elif char == ',' and not in_quotes:
                args.append(current_arg.strip())
                current_arg = ""
            else:
                current_arg += char
                
        # Add the last argument
        if current_arg.strip():
            args.append(current_arg.strip())
        
        # Convert arguments to appropriate types
        parsed_args = []
        for arg in args:
            arg = arg.strip()
            
            # Remove outer quotes from strings
            if (arg.startswith('"') and arg.endswith('"')) or (arg.startswith("'") and arg.endswith("'")):
                parsed_args.append(arg[1:-1])
            # Try to convert to number if possible
            elif arg.lower() == "true":
                parsed_args.append(True)
            elif arg.lower() == "false":
                parsed_args.append(False)
            elif arg.lower() == "null" or arg.lower() == "none":
                parsed_args.append(None)
            else:
                try:
                    # Try to convert to int or float
                    if '.' in arg:
                        parsed_args.append(float(arg))
                    else:
                        parsed_args.append(int(arg))
                except ValueError:
                    # Keep as string if not a number
                    parsed_args.append(arg)
                    
        return parsed_args
    
    def format_result(self, result: Any) -> str:
        """
        Format function result for inclusion in response
        
        Args:
            result: Function execution result
            
        Returns:
            Formatted string representation of the result
        """
        if result is None:
            return "None"
        elif isinstance(result, (dict, list)):
            return json.dumps(result, indent=2)
        else:
            return str(result)
    
    def detect_and_execute_functions(self, text: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Detect function calls in text, execute them, and replace with results
        
        Args:
            text: Input text that may contain function calls
            
        Returns:
            Tuple of (updated text, list of function calls)
        """
        function_calls = []
        
        # Use regex to find function calls
        matches = re.finditer(self.function_pattern, text)
        
        # Process all matches
        offset = 0  # Keep track of string position changes as we modify it
        
        for match in matches:
            # Extract function name and arguments
            func_name = match.group(1)
            args_str = match.group(2)
            
            # Skip if function doesn't exist
            if func_name not in self.functions:
                logger.warning(f"Function '{func_name}' not found, skipping")
                continue
                
            try:
                # Parse arguments
                args = self.parse_arguments(args_str)
                
                # Execute function
                result = execute_function(func_name, args)
                
                # Format the result
                result_str = self.format_result(result)
                
                # Record the function call
                call_info = {
                    "function": func_name,
                    "arguments": args,
                    "result": result
                }
                function_calls.append(call_info)
                self.function_calls.append(call_info)
                
                # Replace function call with result in the text
                start_pos = match.start() + offset
                end_pos = match.end() + offset
                
                original_text = text[start_pos:end_pos]
                new_text = f"{original_text} = {result_str}"
                
                text = text[:start_pos] + new_text + text[end_pos:]
                
                # Update offset for subsequent replacements
                offset += len(new_text) - len(original_text)
                
            except Exception as e:
                logger.error(f"Error executing function {func_name}: {str(e)}")
                # Include error in the response
                start_pos = match.start() + offset
                end_pos = match.end() + offset
                
                original_text = text[start_pos:end_pos]
                new_text = f"{original_text} [ERROR: {str(e)}]"
                
                text = text[:start_pos] + new_text + text[end_pos:]
                
                # Update offset for subsequent replacements
                offset += len(new_text) - len(original_text)
        
        return text, function_calls

    def parse(self, output) -> str:
        """
        Parse the output text, detecting and executing any function calls
        
        Args:
            output: Raw output from the model (can be string or LangChain message object)
            
        Returns:
            Processed output with function calls executed and results included
        """
        # Clear previous function calls
        self.clear_function_calls()
        
        # Handle different types of output objects
        output_text = ""
        
        # If output is a string, use it directly
        if isinstance(output, str):
            output_text = output
        # If it's a LangChain AIMessage or other message type object
        elif hasattr(output, 'content'):
            # Get the content attribute which should contain the message text
            output_text = output.content
        # If it's a dictionary with content
        elif isinstance(output, dict) and 'content' in output:
            output_text = output['content']
        else:
            # Try to convert to string as a fallback
            try:
                output_text = str(output)
                logger.warning(f"Converted unknown output type {type(output)} to string")
            except Exception as e:
                logger.error(f"Failed to convert output to string: {e}")
                return f"[ERROR: Unable to process response of type {type(output)}]"
        
        # Detect and execute functions
        updated_output, _ = self.detect_and_execute_functions(output_text)
        
        # Deduplicate function calls by creating a unique key for each call
        if self.function_calls:
            # Create a dictionary to track unique calls
            unique_calls = {}
            
            for call in self.function_calls:
                # Create a key that uniquely identifies this function call
                # based on function name and arguments
                key = f"{call['function']}|{str(call['arguments'])}"
                
                # Only keep the first occurrence of each unique function call
                if key not in unique_calls:
                    unique_calls[key] = call
            
            # Replace the list with deduplicated calls
            self.function_calls = list(unique_calls.values())
            
            # Log function calls for debugging
            calls = [f"{call['function']}({', '.join(map(str, call['arguments']))})" for call in self.function_calls]
            logger.info(f"Detected and executed {len(calls)} unique function(s): {', '.join(calls)}")
        
        return updated_output
