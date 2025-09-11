#!/bin/bash

# DataLogger Installation Script for Raspberry Pi 5
echo "================================================"
echo "  DataLogger Installation for Raspberry Pi 5"
echo "================================================"

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    echo "Warning: This doesn't appear to be a Raspberry Pi"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system packages
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get install -y python3-pip python3-venv python3-dev
sudo apt-get install -y i2c-tools python3-smbus
sudo apt-get install -y postgresql postgresql-client  # Optional for PostgreSQL

# Enable I2C interface
echo "Enabling I2C interface..."
sudo raspi-config nonint do_i2c 0

# Add user to i2c group
sudo usermod -a -G i2c $USER

# Create project directory
PROJECT_DIR="/home/pi/DataLogger"
if [ ! -d "$PROJECT_DIR" ]; then
    echo "Creating project directory..."
    sudo mkdir -p "$PROJECT_DIR"
    sudo chown -R pi:pi "$PROJECT_DIR"
fi

# Copy project files (assuming script is run from project directory)
echo "Copying project files..."
cp -r . "$PROJECT_DIR/"

# Create virtual environment
cd "$PROJECT_DIR"
echo "Creating Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# Install Python requirements
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r data-logger-project/requirements.txt

# Make scripts executable
chmod +x launch_datalogger.sh

# Install desktop shortcut
if [ -d "/home/pi/Desktop" ]; then
    echo "Installing desktop shortcut..."
    cp datalogger.desktop /home/pi/Desktop/
    chmod +x /home/pi/Desktop/datalogger.desktop
fi

# Install systemd service (optional)
read -p "Install as system service (auto-start on boot)? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing systemd service..."
    sudo cp datalogger.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable datalogger.service
    echo "Service installed. Use 'sudo systemctl start datalogger' to start"
fi

# Create initial configuration
if [ ! -f "config.json" ]; then
    echo "Creating initial configuration..."
    python3 -c "from data-logger-project.config import config; config.save_config()"
fi

echo ""
echo "================================================"
echo "  Installation Complete!"
echo "================================================"
echo ""
echo "To start the DataLogger:"
echo "  1. Desktop: Double-click the DataLogger icon on desktop"
echo "  2. Terminal: Run ./launch_datalogger.sh"
echo "  3. Service: sudo systemctl start datalogger"
echo ""
echo "Access the web interface at: http://localhost:8080"
echo ""
echo "Note: Reboot recommended to ensure all permissions are applied"
echo "Run: sudo reboot"