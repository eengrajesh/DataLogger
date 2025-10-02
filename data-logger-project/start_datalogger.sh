#!/bin/bash
# DataLogger - Double Click Launcher for Raspberry Pi 5
# This script starts the DataLogger application and opens the browser

# Get script directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "========================================"
echo "  DataLogger Startup"
echo "========================================"
echo ""
echo "Working directory: $DIR"
echo ""

# Kill any existing instances
echo "Stopping any existing DataLogger instances..."
pkill -f "python.*app_pi5_final.py" 2>/dev/null
pkill -f "python.*app.py" 2>/dev/null
sleep 1

# Check if Python and app file exist
if [ ! -f "app_pi5_final.py" ]; then
    echo "❌ ERROR: app_pi5_final.py not found!"
    echo "   Current directory: $(pwd)"
    echo ""
    read -p "Press Enter to close..."
    exit 1
fi

# Start application
echo "Starting DataLogger application..."
echo ""
python3 app_pi5_final.py > /tmp/datalogger.log 2>&1 &
APP_PID=$!

# Wait for server to start
echo "Waiting for server to start..."
sleep 5

# Check if app is still running
if ! ps -p $APP_PID > /dev/null 2>&1; then
    echo "❌ ERROR: Application failed to start!"
    echo ""
    echo "Error log:"
    cat /tmp/datalogger.log
    echo ""
    read -p "Press Enter to close..."
    exit 1
fi

echo "✅ Application started (PID: $APP_PID)"
echo ""

# Try different browsers (in order of preference)
echo "Opening browser..."
if command -v chromium-browser &> /dev/null; then
    chromium-browser --new-window http://localhost:8080 &
    echo "✅ Opened in Chromium"
elif command -v firefox &> /dev/null; then
    firefox --new-window http://localhost:8080 &
    echo "✅ Opened in Firefox"
elif command -v x-www-browser &> /dev/null; then
    x-www-browser http://localhost:8080 &
    echo "✅ Opened in default browser"
else
    echo "⚠️  Could not auto-open browser"
    echo "   Please open manually: http://localhost:8080"
fi

echo ""
echo "========================================"
echo "  DataLogger is now running!"
echo "========================================"
echo ""
echo "Dashboard URL: http://localhost:8080"
echo "Application PID: $APP_PID"
echo "Log file: /tmp/datalogger.log"
echo ""
echo "To stop: pkill -f app_pi5_final.py"
echo ""
echo "Press Ctrl+C or close this window to keep running in background"
echo ""

# Keep terminal open
read -p "Press Enter to close this window (app will keep running)..."
