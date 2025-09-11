#!/bin/bash

# DataLogger Launch Script for Raspberry Pi 5
# This script starts the temperature data logging application

echo "================================================"
echo "  DataLogger - Raspberry Pi 5 Temperature Logger"
echo "================================================"

# Navigate to project directory
PROJECT_DIR="/home/pi/DataLogger"
cd "$PROJECT_DIR" || exit 1

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Check and install requirements if needed
echo "Checking dependencies..."
pip install -q -r data-logger-project/requirements.txt

# Start the application
echo "Starting DataLogger Web Interface..."
echo "Access the dashboard at: http://localhost:8080"
echo "Press Ctrl+C to stop the application"
echo ""

# Run the enhanced app
python data-logger-project/app_enhanced.py

# Deactivate virtual environment on exit
deactivate