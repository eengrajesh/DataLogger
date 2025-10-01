#!/bin/bash

# DataLogger Setup Script v2.0 for Raspberry Pi 5
# Handles "externally managed environment" error

echo "============================================"
echo "DataLogger Setup for Raspberry Pi 5 v2.0"
echo "============================================"

# Update system
echo "[1/8] Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
echo "[2/8] Installing system dependencies..."
sudo apt install -y python3-pip python3-venv python3-dev git i2c-tools python3-smbus

# Enable I2C
echo "[3/8] Enabling I2C interface..."
sudo raspi-config nonint do_i2c 0

# Create virtual environment
echo "[4/8] Creating Python virtual environment..."
cd /home/pi/DataLogger
python3 -m venv venv

# Activate virtual environment and install packages
echo "[5/8] Installing Python packages..."
source venv/bin/activate
pip install wheel
pip install -r data-logger-project/requirements.txt

# Create startup script with virtual environment
echo "[6/8] Creating startup script..."
cat > /home/pi/DataLogger/start_datalogger.sh << 'EOF'
#!/bin/bash
cd /home/pi/DataLogger
source venv/bin/activate
python3 data-logger-project/app_pi5_final.py
EOF

chmod +x /home/pi/DataLogger/start_datalogger.sh

# Create systemd service
echo "[7/8] Creating systemd service..."
sudo tee /etc/systemd/system/datalogger.service > /dev/null << EOF
[Unit]
Description=DataLogger Temperature Monitoring
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/DataLogger
ExecStart=/home/pi/DataLogger/start_datalogger.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
echo "[8/8] Enabling auto-start service..."
sudo systemctl daemon-reload
sudo systemctl enable datalogger.service

# Test I2C
echo ""
echo "Testing I2C devices..."
sudo i2cdetect -y 1

echo ""
echo "============================================"
echo "Setup Complete!"
echo "============================================"
echo ""
echo "To start DataLogger manually:"
echo "  cd /home/pi/DataLogger"
echo "  source venv/bin/activate"
echo "  python3 data-logger-project/app_pi5_final.py"
echo ""
echo "To start as service:"
echo "  sudo systemctl start datalogger"
echo ""
echo "To check status:"
echo "  sudo systemctl status datalogger"
echo ""
echo "Access web interface at:"
echo "  http://$(hostname -I | cut -d' ' -f1):8080"
echo ""