#!/bin/bash
# Install DataLogger Desktop Icon
# Run this once to set up double-click launcher

echo "=========================================="
echo "  DataLogger Desktop Icon Installer"
echo "=========================================="

# Get current directory
INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing from: $INSTALL_DIR"

# Make launcher script executable
chmod +x "$INSTALL_DIR/data-logger-project/start_datalogger.sh"

# Create desktop file with correct paths
cat > ~/Desktop/DataLogger.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=DataLogger
Comment=Temperature Data Logger Application
Exec=bash -c 'cd "$INSTALL_DIR/data-logger-project" && ./start_datalogger.sh'
Icon=$INSTALL_DIR/data-logger-project/logo.png
Terminal=true
Categories=Application;Science;
StartupNotify=true
EOF

# Make it executable
chmod +x ~/Desktop/DataLogger.desktop

# Trust the desktop file (required on newer Ubuntu/Raspberry Pi OS)
gio set ~/Desktop/DataLogger.desktop metadata::trusted true 2>/dev/null || true

# Also install to applications menu
mkdir -p ~/.local/share/applications
cp ~/Desktop/DataLogger.desktop ~/.local/share/applications/
chmod +x ~/.local/share/applications/DataLogger.desktop

echo ""
echo "✅ Installation Complete!"
echo ""
echo "Desktop icon installed at: ~/Desktop/DataLogger.desktop"
echo "Using path: $INSTALL_DIR"
echo ""
echo "You can now:"
echo "  1. Double-click 'DataLogger' icon on Desktop"
echo "  2. Find 'DataLogger' in Applications menu"
echo ""
echo "The application will:"
echo "  - Start automatically"
echo "  - Open browser to dashboard"
echo "  - Show terminal output"
echo ""
echo "=========================================="
