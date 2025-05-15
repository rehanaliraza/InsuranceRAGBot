"""
Standalone script to run just the Streamlit dashboard
Use this for troubleshooting if the combined script doesn't work
"""
import os
import subprocess
import sys

# Create metrics directory if it doesn't exist
os.makedirs("metrics", exist_ok=True)

print("Starting Streamlit dashboard...")
print("This may take a few seconds to initialize...")

try:
    # Run Streamlit directly (not as a background process)
    # This will keep the console output visible
    if sys.platform == 'win32':
        streamlit_cmd = [sys.executable, "-m", "streamlit", "run", "dashboard.py"]
    else:
        streamlit_cmd = ["streamlit", "run", "dashboard.py"]
        
    # Run the process in the foreground so we can see any errors
    process = subprocess.run(streamlit_cmd)
    
except Exception as e:
    print(f"Error running Streamlit: {str(e)}")
    print("\nTroubleshooting tips:")
    print("1. Make sure streamlit is installed: pip install streamlit")
    print("2. Check if port 8501 is already in use:")
    if sys.platform == 'win32':
        print("   - Run: netstat -ano | findstr :8501")
        print("   - Then: taskkill /PID <PID> /F")
    else:
        print("   - Run: lsof -i :8501")
        print("   - Then: kill -9 <PID>")
    print("3. Try running streamlit directly: streamlit run dashboard.py")
    print("4. Check your firewall settings to ensure Streamlit is allowed") 