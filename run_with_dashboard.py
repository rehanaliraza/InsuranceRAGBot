"""
Run General-Purpose RAG Bot with Metrics Dashboard - Python launcher
Windows-compatible alternative to run_with_dashboard.sh
"""
import os
import subprocess
import signal
import time
import sys
import atexit

# Create metrics directory if it doesn't exist
os.makedirs("metrics", exist_ok=True)

# Process holders
app_process = None
dashboard_process = None

def cleanup():
    """Kill processes when script is terminated"""
    print("\nShutting down...")
    if app_process:
        if sys.platform == 'win32':
            app_process.kill()
        else:
            os.killpg(os.getpgid(app_process.pid), signal.SIGTERM)
    
    if dashboard_process:
        if sys.platform == 'win32':
            dashboard_process.kill()
        else:
            os.killpg(os.getpgid(dashboard_process.pid), signal.SIGTERM)

# Register cleanup handler
atexit.register(cleanup)

try:
    # Start the main application
    print("Starting General-Purpose RAG Bot...")
    
    if sys.platform == 'win32':
        app_process = subprocess.Popen([sys.executable, "run_mcp.py"], 
                                        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
    else:
        app_process = subprocess.Popen([sys.executable, "run_mcp.py"], 
                                       start_new_session=True)
    
    # Wait a moment for the app to initialize
    time.sleep(3)
    
    # Start the dashboard
    print("Starting Metrics Dashboard...")
    
    if sys.platform == 'win32':
        dashboard_process = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "dashboard.py"],
                                           creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
    else:
        dashboard_process = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "dashboard.py"],
                                           start_new_session=True)
    
    print("\nInsuranceRAGBot and Dashboard are running!")
    print("- Main application: http://localhost:8000")
    print("- Metrics dashboard: http://localhost:8501")
    print("\nPress Ctrl+C to shut down both applications")
    
    # Keep the script running
    while True:
        time.sleep(1)
        
except KeyboardInterrupt:
    # Will trigger cleanup via atexit handler
    pass 