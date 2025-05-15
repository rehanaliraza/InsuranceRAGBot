"""
Reset all metrics data
Use this script to completely reset all metrics
"""
import os
import shutil

def reset_metrics():
    """Reset all metrics data"""
    metrics_dir = "metrics"
    
    if not os.path.exists(metrics_dir):
        print(f"Metrics directory not found: {metrics_dir}")
        return
    
    # Create backups directory
    backup_dir = os.path.join(metrics_dir, "backups")
    os.makedirs(backup_dir, exist_ok=True)
    
    # Timestamp for backup
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Backup existing files
    files_backed_up = 0
    metrics_files = [f for f in os.listdir(metrics_dir) if f.endswith(".jsonl")]
    
    for filename in metrics_files:
        src_path = os.path.join(metrics_dir, filename)
        dst_path = os.path.join(backup_dir, f"{filename}_{timestamp}")
        
        try:
            shutil.copy2(src_path, dst_path)
            os.remove(src_path)
            files_backed_up += 1
            print(f"Backed up and removed: {src_path}")
        except Exception as e:
            print(f"Error processing {src_path}: {str(e)}")
    
    print(f"\nReset complete! {files_backed_up} metrics files have been reset.")
    if files_backed_up > 0:
        print(f"Backups saved to: {backup_dir}")
    
    # Create empty files to ensure directory structure is maintained
    empty_files = ["latency.jsonl", "token_usage.jsonl", "retrieval.jsonl", "agent_usage.jsonl"]
    for filename in empty_files:
        with open(os.path.join(metrics_dir, filename), 'w') as f:
            pass
        print(f"Created empty file: {os.path.join(metrics_dir, filename)}")

if __name__ == "__main__":
    print("This will reset ALL metrics data. Existing data will be backed up.")
    confirm = input("Are you sure you want to proceed? (y/n): ")
    
    if confirm.lower() in ['y', 'yes']:
        reset_metrics()
    else:
        print("Operation canceled.") 