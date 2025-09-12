#!/bin/bash

# DataLogger Pi5 Setup Script
# Run this script on your Raspberry Pi 5

echo "🌡️ DataLogger Pi5 Setup Starting..."
echo "======================================"

# Check if running on Pi
if ! command -v raspi-config &> /dev/null; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Enable I2C
echo "🔧 Enabling I2C interface..."
sudo raspi-config nonint do_i2c 0

# Install system dependencies
echo "📚 Installing Python dependencies..."
sudo apt install -y python3-pip python3-venv python3-smbus python3-dev

# Create project directory if it doesn't exist
PROJECT_DIR="$HOME/DataLogger"
if [ ! -d "$PROJECT_DIR" ]; then
    echo "📁 Cloning DataLogger repository..."
    cd "$HOME"
    git clone https://github.com/eengrajesh/DataLogger.git
else
    echo "📁 DataLogger directory already exists, pulling latest changes..."
    cd "$PROJECT_DIR"
    git pull origin main
fi

cd "$PROJECT_DIR/data-logger-project"

# Install Python packages
echo "🐍 Installing Python packages..."
pip install --break-system-packages -r requirements.txt

# Create default config if it doesn't exist
if [ ! -f "config.json" ]; then
    echo "⚙️  Creating default configuration..."
    cat > config.json << 'EOF'
{
    "telegram": {
        "bot_token": "",
        "authorized_users": [],
        "admin_users": [],
        "group_chat_id": null
    },
    "hardware": {
        "i2c_bus": 1,
        "daq_address": 22,
        "enable_gpio": false
    },
    "logging": {
        "default_interval": 5,
        "enable_text_logging": true,
        "enable_database": true
    }
}
EOF
    echo "📝 Config file created at: $(pwd)/config.json"
    echo "   Please edit it with your Telegram bot token and user ID"
fi

# Test I2C
echo "🔍 Testing I2C interface..."
if command -v i2cdetect &> /dev/null; then
    echo "I2C devices detected:"
    sudo i2cdetect -y 1
else
    echo "⚠️  i2c-tools not installed, installing now..."
    sudo apt install -y i2c-tools
    echo "I2C devices detected:"
    sudo i2cdetect -y 1
fi

# Create systemd service
echo "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/datalogger.service > /dev/null << EOF
[Unit]
Description=DataLogger Temperature Monitoring
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=$PROJECT_DIR/data-logger-project
ExecStart=/usr/bin/python3 app.py
Restart=always
RestartSec=10
Environment=PYTHONPATH=$PROJECT_DIR/data-logger-project

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload

echo ""
echo "✅ Setup Complete!"
echo "=================="
echo ""
echo "📝 Next Steps:"
echo "1. Edit config.json with your Telegram bot settings:"
echo "   nano $PROJECT_DIR/data-logger-project/config.json"
echo ""
echo "2. Test the application:"
echo "   cd $PROJECT_DIR/data-logger-project"
echo "   python test_connection.py"
echo ""
echo "3. Start the service:"
echo "   sudo systemctl enable datalogger.service"
echo "   sudo systemctl start datalogger.service"
echo ""
echo "4. Check service status:"
echo "   sudo systemctl status datalogger.service"
echo ""
echo "5. Access web interface:"
echo "   http://$(hostname -I | cut -d' ' -f1):8080"
echo ""
echo "6. View logs:"
echo "   sudo journalctl -u datalogger.service -f"
echo ""

# Ask if user wants to run test
read -p "🧪 Run connection test now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Running connection test..."
    python test_connection.py
fi

echo ""
echo "🌡️ DataLogger setup complete! Happy temperature monitoring! 🚀"