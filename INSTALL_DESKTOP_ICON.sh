#!/bin/bash
# Install DataLogger Desktop Icon
# Run this once to set up double-click launcher

echo "=========================================="
echo "  DataLogger Desktop Icon Installer"
echo "=========================================="

# Make launcher script executable
chmod +x data-logger-project/start_datalogger.sh

# Copy desktop file to Desktop
cp DataLogger.desktop ~/Desktop/
chmod +x ~/Desktop/DataLogger.desktop

# Also install to applications menu
mkdir -p ~/.local/share/applications
cp DataLogger.desktop ~/.local/share/applications/
chmod +x ~/.local/share/applications/DataLogger.desktop

echo ""
echo "✅ Installation Complete!"
echo ""
echo "You can now:"
echo "  1. Double-click 'DataLogger' icon on Desktop"
echo "  2. Find 'DataLogger' in Applications menu"
echo ""
echo "The application will:"
echo "  - Start automatically"
echo "  - Open browser to dashboard"
echo "  - Run in background"
echo ""
echo "=========================================="
