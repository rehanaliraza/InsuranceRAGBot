import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Get API key from environment
api_key = os.getenv("OPENAI_API_KEY")

# Check if API key is available
if not api_key:
    print("Error: OPENAI_API_KEY not found in .env file")
    print("Please add your OpenAI API key to the .env file")
    exit(1)

# Initialize the client
client = OpenAI(api_key=api_key)

# Test a simple completion
try:
    print("Testing OpenAI API connection...")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, are you working?"}
        ]
    )
    print(f"API response: {response.choices[0].message.content}")
    print("OpenAI API test successful!")
except Exception as e:
    print(f"Error connecting to OpenAI API: {e}") 