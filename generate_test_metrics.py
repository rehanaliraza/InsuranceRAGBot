"""
Generate test metrics data to populate the dashboard charts
"""
import os
import json
import random
from datetime import datetime, timedelta
import time
import uuid

# Create metrics directory if it doesn't exist
METRICS_DIR = os.path.join("metrics")
os.makedirs(METRICS_DIR, exist_ok=True)

# File paths
LATENCY_FILE = os.path.join(METRICS_DIR, "latency.jsonl")
TOKEN_USAGE_FILE = os.path.join(METRICS_DIR, "token_usage.jsonl")
RETRIEVAL_METRICS_FILE = os.path.join(METRICS_DIR, "retrieval.jsonl")
AGENT_USAGE_FILE = os.path.join(METRICS_DIR, "agent_usage.jsonl")

# Generate data for the past 3 hours with 5-minute intervals
def generate_test_data():
    # Clear existing files
    for file in [LATENCY_FILE, TOKEN_USAGE_FILE, RETRIEVAL_METRICS_FILE, AGENT_USAGE_FILE]:
        if os.path.exists(file):
            os.remove(file)

    # Generate timestamps for the past 3 hours with 5-minute intervals
    now = datetime.now()
    timestamps = []
    for i in range(36):  # 3 hours * 12 intervals per hour = 36
        timestamp = now - timedelta(minutes=5 * i)
        timestamps.append(timestamp.isoformat())
    
    # Agent types to simulate
    agent_types = ["developer", "writer", "tester", "sales", "system"]
    
    # Operations to simulate
    operations = ["routing", "retrieval", "llm_response", "total", "system_response"]
    
    # Query types to simulate
    query_types = ["direct", "routed"]
    
    # Generate latency data
    print("Generating latency data...")
    for timestamp in timestamps:
        for _ in range(random.randint(1, 3)):  # 1-3 queries per timestamp
            query_id = f"query_{uuid.uuid4().hex[:8]}"
            agent_type = random.choice(agent_types)
            
            # Generate latency for different operations
            for operation in operations:
                if operation == "system_response" and agent_type != "system":
                    continue
                    
                # Skip some operations randomly to simulate real-world usage
                if random.random() < 0.3:  # 30% chance to skip
                    continue
                    
                # Generate realistic latency values
                if operation == "routing":
                    latency = random.uniform(0.01, 0.1)
                elif operation == "retrieval":
                    latency = random.uniform(0.5, 1.5)
                elif operation == "llm_response":
                    latency = random.uniform(2.0, 5.0)
                elif operation == "total":
                    latency = random.uniform(3.0, 7.0)
                else:  # system_response
                    latency = random.uniform(0.05, 0.2)
                
                data = {
                    "timestamp": timestamp,
                    "operation": operation,
                    "agent_type": agent_type,
                    "latency": latency,
                    "query_id": query_id
                }
                
                with open(LATENCY_FILE, 'a') as f:
                    f.write(json.dumps(data) + '\n')
    
    # Generate token usage data
    print("Generating token usage data...")
    for timestamp in timestamps:
        for _ in range(random.randint(1, 3)):  # 1-3 queries per timestamp
            query_id = f"query_{uuid.uuid4().hex[:8]}"
            agent_type = random.choice(agent_types)
            
            # Skip system agent for token usage (it doesn't use the LLM)
            if agent_type == "system":
                continue
                
            # Generate realistic token values
            prompt_tokens = random.randint(500, 2000)
            completion_tokens = random.randint(200, 800)
            
            # Model names based on agent type
            model = "gpt-4" if agent_type != "router" else "gpt-3.5-turbo"
            
            data = {
                "timestamp": timestamp,
                "agent_type": agent_type,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
                "model": model,
                "query_id": query_id
            }
            
            with open(TOKEN_USAGE_FILE, 'a') as f:
                f.write(json.dumps(data) + '\n')
    
    # Generate retrieval metrics data
    print("Generating retrieval metrics data...")
    for timestamp in timestamps:
        for _ in range(random.randint(1, 3)):  # 1-3 queries per timestamp
            query_id = f"query_{uuid.uuid4().hex[:8]}"
            query = f"Sample query {random.randint(1, 100)}"
            num_docs = random.randint(2, 15)
            
            data = {
                "timestamp": timestamp,
                "query": query,
                "num_docs_retrieved": num_docs,
                "query_id": query_id
            }
            
            with open(RETRIEVAL_METRICS_FILE, 'a') as f:
                f.write(json.dumps(data) + '\n')
    
    # Generate agent usage data
    print("Generating agent usage data...")
    for timestamp in timestamps:
        for _ in range(random.randint(1, 3)):  # 1-3 queries per timestamp
            query_id = f"query_{uuid.uuid4().hex[:8]}"
            agent_type = random.choice(agent_types)
            query_type = random.choice(query_types)
            
            data = {
                "timestamp": timestamp,
                "agent_type": agent_type,
                "query_type": query_type,
                "query_id": query_id
            }
            
            with open(AGENT_USAGE_FILE, 'a') as f:
                f.write(json.dumps(data) + '\n')
    
    print("Test data generation complete!")
    print(f"Generated data across {len(timestamps)} timestamps")
    print("Restart the dashboard to see the populated charts")

if __name__ == "__main__":
    generate_test_data() 