#!/usr/bin/env python3
"""
Test script for custom functions in InsuranceRAGBot
"""
import os
import sys

# Add the current directory to path if not already there
current_dir = os.path.abspath(os.path.dirname(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from app.utils.custom_functions import CUSTOM_FUNCTIONS, execute_function

def test_custom_functions():
    """Test all custom functions directly"""
    print("\n" + "="*80)
    print("TESTING CUSTOM FUNCTIONS")
    print("="*80)
    
    # Test each function in CUSTOM_FUNCTIONS
    for func_name, func in CUSTOM_FUNCTIONS.items():
        print(f"\nTesting function: {func_name}")
        
        # Sample arguments for each function
        sample_args = {
            "premOp": [5, 3],
            "yatiOp": [10],
            "factorial": [5],
            "get_weather": ["London"],
            "translate_text": ["hello", "es"],
            "calculate_mortgage": [200000, 0.045, 30],
            "extract_numbers": ["The price is $19.99 and quantity is 5"]
        }
        
        # Get sample arguments for this function
        args = sample_args.get(func_name, [])
        
        try:
            # Execute the function with sample arguments
            result = execute_function(func_name, args)
            print(f"  Arguments: {args}")
            print(f"  Result: {result}")
            print(f"  Success: Function executed correctly")
        except Exception as e:
            print(f"  Error: {str(e)}")
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80 + "\n")

if __name__ == "__main__":
    test_custom_functions()
