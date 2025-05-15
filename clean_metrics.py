"""
Clean metrics data - remove fabricated test data while preserving real metrics
"""
import os
import json
from datetime import datetime, timedelta

# Metrics directory
METRICS_DIR = os.path.join("metrics")

# File paths
LATENCY_FILE = os.path.join(METRICS_DIR, "latency.jsonl")
TOKEN_USAGE_FILE = os.path.join(METRICS_DIR, "token_usage.jsonl")
RETRIEVAL_METRICS_FILE = os.path.join(METRICS_DIR, "retrieval.jsonl")
AGENT_USAGE_FILE = os.path.join(METRICS_DIR, "agent_usage.jsonl")

def backup_file(file_path):
    """Create a backup of the original file if it exists"""
    if os.path.exists(file_path):
        backup_path = f"{file_path}.bak"
        with open(file_path, 'r') as src, open(backup_path, 'w') as dst:
            dst.write(src.read())
        print(f"Created backup: {backup_path}")
        return True
    return False

def clean_metrics_file(file_path):
    """Remove potentially fabricated data from the metrics file"""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    
    # Backup the file first
    if not backup_file(file_path):
        return
    
    # Determine cutoff timestamp (test data was generated for past 3 hours with many entries)
    # Real data typically has fewer entries spaced further apart
    cutoff_time = datetime.now() - timedelta(hours=3)
    
    # Read all data
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            if line.strip():
                try:
                    entry = json.loads(line)
                    data.append(entry)
                except json.JSONDecodeError:
                    # Skip invalid JSON lines
                    pass
    
    print(f"Read {len(data)} entries from {file_path}")
    
    if len(data) == 0:
        print(f"No data to clean in {file_path}")
        return
    
    # Sort data by timestamp
    data.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    # Analyze data to find potential test data patterns
    timestamps = {}
    for entry in data:
        timestamp = entry.get('timestamp', '')
        if timestamp:
            timestamps[timestamp] = timestamps.get(timestamp, 0) + 1
    
    # If there are timestamps with unusually high entry counts, they're likely test data
    # Real usage typically has only a few entries per timestamp
    high_frequency_timestamps = set()
    for timestamp, count in timestamps.items():
        if count > 5:  # If more than 5 entries share the same timestamp, it's suspicious
            high_frequency_timestamps.add(timestamp)
    
    # Look for suspiciously regular patterns in timestamps (every 5 mins)
    # Convert to datetime objects for timestamp analysis
    datetime_timestamps = []
    for ts in timestamps.keys():
        try:
            dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
            datetime_timestamps.append(dt)
        except (ValueError, TypeError):
            pass
    
    datetime_timestamps.sort()
    
    # Check for regular 5-minute intervals in consecutive timestamps
    if len(datetime_timestamps) >= 3:
        regular_pattern_timestamps = set()
        for i in range(len(datetime_timestamps) - 2):
            diff1 = (datetime_timestamps[i+1] - datetime_timestamps[i]).total_seconds()
            diff2 = (datetime_timestamps[i+2] - datetime_timestamps[i+1]).total_seconds()
            
            # If intervals are almost exactly 5 minutes (300 seconds), flag them
            if abs(diff1 - 300) < 10 and abs(diff2 - 300) < 10:
                regular_pattern_timestamps.add(datetime_timestamps[i].isoformat())
                regular_pattern_timestamps.add(datetime_timestamps[i+1].isoformat())
                regular_pattern_timestamps.add(datetime_timestamps[i+2].isoformat())
    
        # Add these to high frequency timestamps
        for ts in regular_pattern_timestamps:
            high_frequency_timestamps.add(ts)
    
    # Filter out suspicious data
    filtered_data = []
    for entry in data:
        timestamp = entry.get('timestamp', '')
        
        # Skip entries with suspicious timestamps
        if timestamp in high_frequency_timestamps:
            continue
            
        # Skip entries with query_id starting with "query_" (used in test data)
        query_id = entry.get('query_id', '')
        if query_id.startswith('query_') and len(query_id) > 15:
            continue
            
        filtered_data.append(entry)
    
    print(f"Filtered out {len(data) - len(filtered_data)} suspicious entries")
    
    # Write filtered data back to file
    with open(file_path, 'w') as f:
        for entry in filtered_data:
            f.write(json.dumps(entry) + '\n')
    
    print(f"Saved {len(filtered_data)} entries to {file_path}")

def main():
    print("Cleaning metrics files...")
    
    # Make sure metrics directory exists
    if not os.path.exists(METRICS_DIR):
        print(f"Metrics directory not found: {METRICS_DIR}")
        return
    
    # Clean each metrics file
    clean_metrics_file(LATENCY_FILE)
    clean_metrics_file(TOKEN_USAGE_FILE)
    clean_metrics_file(RETRIEVAL_METRICS_FILE)
    clean_metrics_file(AGENT_USAGE_FILE)
    
    print("\nMetrics cleaning complete!")
    print("Restart the dashboard to see the cleaned data")
    print("\nIf you need to restore the original data, use the .bak files in the metrics directory")

if __name__ == "__main__":
    main() 