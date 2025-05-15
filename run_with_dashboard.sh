#!/bin/bash

# Run the InsuranceRAGBot with Metrics Dashboard

# Create metrics directory if it doesn't exist
mkdir -p metrics

echo "Starting InsuranceRAGBot..."
# Run the main application in the background
python run_mcp.py &
APP_PID=$!

# Wait a moment for the app to initialize
sleep 3

echo "Starting Metrics Dashboard..."
# Run the Streamlit dashboard
streamlit run dashboard.py &
DASHBOARD_PID=$!

# Function to handle script termination
function cleanup {
    echo "Shutting down..."
    kill $APP_PID
    kill $DASHBOARD_PID
    exit 0
}

# Register the cleanup function for SIGINT (Ctrl+C) and SIGTERM
trap cleanup SIGINT SIGTERM

echo "InsuranceRAGBot and Dashboard are running!"
echo "- Main application: http://localhost:8000"
echo "- Metrics dashboard: http://localhost:8501"
echo ""
echo "Press Ctrl+C to shut down both applications"

# Keep the script running
wait 