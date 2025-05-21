import requests
import json

def test_query_endpoint():
    url = "http://localhost:8000/api/query"
    payload = {
        "query": "What are the key elements of effective documentation?"
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    print("Testing /api/query endpoint...")
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Status: Success")
        print(f"Agent: {data['agent']}")
        print(f"Response: {data['response']}")
    else:
        print(f"Status: Failed (Status code: {response.status_code})")
        print(f"Error: {response.text}")

def test_review_endpoint():
    url = "http://localhost:8000/api/review"
    payload = {
        "query": "What are the benefits of knowledge management?"
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    print("\nTesting /api/review endpoint...")
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Status: Success")
        print(f"Primary Agent: {data['primary_agent']}")
        print(f"Response: {data['response']}")
        print(f"Validation: {data['validation']}")
    else:
        print(f"Status: Failed (Status code: {response.status_code})")
        print(f"Error: {response.text}")

if __name__ == "__main__":
    print("API Test Script")
    print("---------------")
    test_query_endpoint()
    test_review_endpoint() 