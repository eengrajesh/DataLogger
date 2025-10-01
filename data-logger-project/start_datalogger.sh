#!/bin/bash
# DataLogger - Double Click Launcher for Raspberry Pi 5
# This script starts the DataLogger application and opens the browser

# Get script directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Kill any existing instances
pkill -f "python.*app_pi5_final.py" 2>/dev/null
pkill -f "python.*app.py" 2>/dev/null

# Start application in background
echo "Starting DataLogger..."
python3 app_pi5_final.py > /tmp/datalogger.log 2>&1 &

# Wait for server to start
sleep 3

# Open browser
echo "Opening dashboard..."
chromium-browser --new-window http://localhost:8080 &

echo "DataLogger started! Check browser window."
echo "To stop: run 'pkill -f app_pi5_final.py'"
