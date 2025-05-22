"""
Custom Functions Module - Provides specialized functions for the InsuranceRAGBot

This module allows you to define custom functions that the bot can detect and execute
based on user queries. Functions can perform calculations, API calls, data processing,
or any other operations that aren't built into the language model.

Usage:
1. Define your function with proper type hints and docstrings
2. Add it to the CUSTOM_FUNCTIONS dictionary with its name as the key
3. The bot will automatically detect and use these functions when needed

Example:
    When a user asks "What is premOp(5,3)?", the bot will:
    1. Detect the function call pattern
    2. Look up the function "premOp" in the CUSTOM_FUNCTIONS dictionary
    3. Execute the function with arguments (5,3)
    4. Include the result in the response
"""
import requests
import json
import math
import random
from typing import Any, Dict, List, Union, Optional
import logging

# Setup logging
logger = logging.getLogger("custom_functions")

def premOp(a: float, b: float) -> float:
    """
    Custom operation that adds a plus twice b
    
    Args:
        a: First number
        b: Second number (will be multiplied by 2)
        
    Returns:
        a + 2*b
    
    Example:
        premOp(4, 1) = 4 + 2*1 = 6
    """
    logger.info(f"Executing premOp({a}, {b})")
    result = a + 2 * b
    return result

def latin_api() -> Dict[str, Any]:
    """
    Fetches data from a public API and returns the result.
    
    Args:
        None
        
    Returns:
        Dictionary containing the API response data
        
    Example:
        latin_api() -> {'userId': 1, 'id': 1, 'title': '...', 'body': '...'}
    """
    logger.info(f"Executing latin_api()")
    url = 'https://jsonplaceholder.typicode.com/posts/1'  # Sample API endpoint

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        data = response.json()  # Parse the JSON response
        logger.info(f"latin_api result: {data}")
        return data

    except requests.exceptions.RequestException as e:
        logger.error(f"Error in latin_api: {e}")
        return None

def factorial(n: int) -> int:
    """
    Calculate the factorial of a number
    
    Args:
        n: Non-negative integer
        
    Returns:
        n! (n factorial)
        
    Example:
        factorial(5) = 5 * 4 * 3 * 2 * 1 = 120
    """
    if not isinstance(n, int) or n < 0:
        raise ValueError("Input must be a non-negative integer")
    
    logger.info(f"Executing factorial({n})")
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)

def get_weather(city: str) -> Dict[str, Any]:
    """
    Get current weather information for a city using a public API
    
    Args:
        city: Name of the city
        
    Returns:
        Dictionary with weather information
        
    Example:
        get_weather("London")
    """
    logger.info(f"Executing get_weather({city})")
    
    # This uses a mock response instead of a real API call
    # In a production environment, you would use a real weather API
    weather_data = {
        "location": city,
        "temperature": round(random.uniform(0, 35), 1),
        "conditions": random.choice(["Sunny", "Cloudy", "Rainy", "Snowy"]),
        "humidity": round(random.uniform(30, 100)),
        "wind_speed": round(random.uniform(0, 30), 1)
    }
    
    return weather_data

def translate_text(text: str, target_language: str) -> str:
    """
    Translate text to another language (mock implementation)
    
    Args:
        text: Text to translate
        target_language: Target language code (e.g., 'es' for Spanish)
        
    Returns:
        Translated text
        
    Example:
        translate_text("Hello", "es") -> "Hola"
    """
    logger.info(f"Executing translate_text({text}, {target_language})")
    
    # Mock translations - in a real implementation, this would call a translation API
    translations = {
        "es": {
            "hello": "hola",
            "goodbye": "adiós",
            "thank you": "gracias"
        },
        "fr": {
            "hello": "bonjour",
            "goodbye": "au revoir",
            "thank you": "merci"
        },
        "de": {
            "hello": "hallo",
            "goodbye": "auf wiedersehen",
            "thank you": "danke"
        }
    }
    
    # Simple mock implementation
    if target_language in translations and text.lower() in translations[target_language]:
        return translations[target_language][text.lower()]
    
    # Return original with a note that this is a mock
    return f"[MOCK TRANSLATION to {target_language}]: {text}"

def calculate_mortgage(principal: float, interest_rate: float, years: int) -> Dict[str, Any]:
    """
    Calculate monthly mortgage payment and total interest
    
    Args:
        principal: Loan amount
        interest_rate: Annual interest rate (as decimal, e.g., 0.05 for 5%)
        years: Loan term in years
        
    Returns:
        Dictionary with monthly payment and total interest paid
        
    Example:
        calculate_mortgage(200000, 0.045, 30)
    """
    logger.info(f"Executing calculate_mortgage({principal}, {interest_rate}, {years})")
    
    # Monthly interest rate
    monthly_rate = interest_rate / 12
    
    # Total number of payments
    payments = years * 12
    
    # Calculate monthly payment using the mortgage formula
    if monthly_rate == 0:
        monthly_payment = principal / payments
    else:
        monthly_payment = principal * (monthly_rate * (1 + monthly_rate) ** payments) / ((1 + monthly_rate) ** payments - 1)
    
    # Calculate total payment and interest
    total_payment = monthly_payment * payments
    total_interest = total_payment - principal
    
    return {
        "monthly_payment": round(monthly_payment, 2),
        "total_payment": round(total_payment, 2),
        "total_interest": round(total_interest, 2)
    }

def extract_numbers(text: str) -> List[float]:
    """
    Extract all numbers from a text string
    
    Args:
        text: Input text containing numbers
        
    Returns:
        List of numbers found in the text
        
    Example:
        extract_numbers("The price is $19.99 and quantity is 5") -> [19.99, 5]
    """
    logger.info(f"Executing extract_numbers({text})")
    
    import re
    # Find all numbers (integers and floats) in the text
    pattern = r'-?\d+\.\d+|-?\d+'
    matches = re.findall(pattern, text)
    
    # Convert string matches to float
    numbers = [float(match) for match in matches]
    return numbers

# Dictionary of all available custom functions
# Key: Function name as it will be called in queries
# Value: Function reference
CUSTOM_FUNCTIONS = {
    "premOp": premOp,
    "latin_api": latin_api,
    "factorial": factorial,
    "get_weather": get_weather,
    "translate_text": translate_text,
    "calculate_mortgage": calculate_mortgage,
    "extract_numbers": extract_numbers
}

def get_function_descriptions() -> Dict[str, str]:
    """Get descriptions of all available custom functions"""
    descriptions = {}
    for name, func in CUSTOM_FUNCTIONS.items():
        doc = func.__doc__.strip() if func.__doc__ else "No description available"
        # Extract the first line of the docstring for a brief description
        brief_desc = doc.split('\n')[0].strip()
        descriptions[name] = brief_desc
    return descriptions

def get_function_details() -> Dict[str, Dict[str, Any]]:
    """Get detailed information about all available custom functions"""
    details = {}
    for name, func in CUSTOM_FUNCTIONS.items():
        doc = func.__doc__.strip() if func.__doc__ else "No description available"
        details[name] = {
            "description": doc,
            "name": name
        }
    return details

def execute_function(function_name: str, args: List[Any]) -> Any:
    """
    Execute a custom function by name with the provided arguments
    
    Args:
        function_name: Name of the function to execute
        args: List of arguments to pass to the function
        
    Returns:
        Result of the function execution
    """
    if function_name not in CUSTOM_FUNCTIONS:
        raise ValueError(f"Function '{function_name}' not found")
    
    function = CUSTOM_FUNCTIONS[function_name]
    logger.info(f"Executing {function_name} with args: {args}")
    
    try:
        result = function(*args)
        logger.info(f"{function_name} result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error executing {function_name}: {str(e)}")
        raise
