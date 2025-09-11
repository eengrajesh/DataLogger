# Feature Requirements for DataLogger Enhancement

## 1. Graphical Representation Improvements

### Current Issues:
- Graph visualization needs improvement for better readability
- Need better real-time updating charts

### Proposed Solutions:
```python
# Use Chart.js or Plotly for better graphs
# Options:
1. Plotly.js - Interactive graphs with zoom, pan, export
2. Chart.js - Lightweight, responsive charts
3. Highcharts - Professional time-series charts
4. D3.js - Fully customizable visualizations

# Implementation approach:
- Add time-series graph with configurable time windows (1h, 6h, 24h, 7d)
- Add min/max/average indicators
- Add zoom and pan capabilities
- Add export graph as image feature
- Color-coded channels for easy identification
```

## 2. Text File Storage System

### Requirements:
- Store data in text files first before database
- Rotating log files (daily/hourly)
- Automatic file management

### Implementation:
```python
# File structure:
/data/
  /raw/
    2024-01-15_00.txt  # Hourly files
    2024-01-15_01.txt
  /daily/
    2024-01-15.txt     # Daily consolidated

# Format:
# timestamp,channel,temperature,calibrated_temp
2024-01-15 10:30:45,1,23.5,23.7
2024-01-15 10:30:45,2,24.1,24.3

# Code snippet:
import os
from datetime import datetime

class TextFileLogger:
    def __init__(self, base_path="/home/pi/datalogger/data"):
        self.base_path = base_path
        
    def write_reading(self, channel, temp, calibrated_temp):
        timestamp = datetime.now()
        filename = f"{timestamp.strftime('%Y-%m-%d_%H')}.txt"
        filepath = os.path.join(self.base_path, "raw", filename)
        
        with open(filepath, 'a') as f:
            f.write(f"{timestamp},{channel},{temp},{calibrated_temp}\n")
```

## 3. CSV Download with Text File Source

### Features:
- Download data from text files
- Filter by date range
- Filter by channels
- Compress large files

### API Endpoints:
```python
# Download endpoint
@app.route('/api/download/csv', methods=['POST'])
def download_csv():
    # Parameters:
    # - start_date
    # - end_date  
    # - channels[]
    # - include_raw (true/false)
    
    # Read from text files
    # Generate CSV
    # Return as download
    
# Implementation:
import csv
from flask import send_file
import zipfile

def generate_csv_from_text(start_date, end_date, channels):
    # Read text files in date range
    # Filter by channels
    # Write to CSV
    # Zip if > 10MB
    pass
```

## 4. Push Button GPIO Control

### Physical Button Functions:
```python
# GPIO Button Configuration
import RPi.GPIO as GPIO

BUTTON_PINS = {
    'START_LOGGING': 17,    # Green button - Start logging
    'STOP_LOGGING': 27,     # Red button - Stop logging
    'SHUTDOWN': 22,         # Power button - Safe shutdown
    'EXPORT_USB': 23,       # Blue button - Export to USB
    'WIFI_RESET': 24        # Reset WiFi settings
}

# LED Indicators
LED_PINS = {
    'STATUS': 5,            # Green - Running
    'ERROR': 6,             # Red - Error
    'NETWORK': 13,          # Blue - Network connected
    'LOGGING': 19           # Yellow - Logging active
}

# Implementation:
class GPIOController:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        self.setup_buttons()
        self.setup_leds()
        
    def setup_buttons(self):
        for pin in BUTTON_PINS.values():
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(pin, GPIO.FALLING, 
                                callback=self.button_callback, 
                                bouncetime=300)
    
    def button_callback(self, channel):
        if channel == BUTTON_PINS['START_LOGGING']:
            self.start_logging()
        elif channel == BUTTON_PINS['SHUTDOWN']:
            self.safe_shutdown()
```

## 5. WiFi/Bluetooth Mobile Connectivity

### A. WiFi Access Point Mode:
```bash
# Setup Pi as WiFi Access Point
# Install hostapd and dnsmasq
sudo apt-get install hostapd dnsmasq

# Configure as AP when no network available
# SSID: DataLogger_[MAC]
# Password: Auto-generated or fixed
```

### B. Bluetooth Configuration:
```python
# Bluetooth LE Advertisement
import bluetooth

class BluetoothBeacon:
    def __init__(self):
        self.setup_ble()
        
    def advertise_service(self):
        # Advertise datalogger service
        # Include IP address in advertisement
        # Allow pairing for configuration
        pass

# Mobile App Connection:
# 1. Scan for BLE devices
# 2. Connect to DataLogger
# 3. Get WiFi credentials
# 4. Configure via BLE
```

### C. Mobile App Features:
```
1. Auto-discovery via mDNS/Bonjour
   - datalogger.local
   
2. QR Code for quick connect
   - Generate QR with WiFi credentials
   - Display on small OLED screen
   
3. Companion App (React Native/Flutter)
   - Scan for devices
   - Configure settings
   - View real-time data
   - Download logs
```

## 6. Board Online Status Monitoring

### Methods to Check Online Status:

```python
# 1. Heartbeat Server
class HeartbeatMonitor:
    def __init__(self):
        self.last_heartbeat = datetime.now()
        
    def send_heartbeat(self):
        # Options:
        # a. MQTT broker
        # b. WebSocket to server
        # c. HTTP POST to monitoring service
        # d. UDP broadcast on local network
        pass

# 2. mDNS/Avahi Service
# Install: sudo apt-get install avahi-daemon
# Broadcast as: datalogger.local

# 3. Telegram Bot Integration
import telepot

bot = telepot.Bot('YOUR_BOT_TOKEN')

def send_status():
    bot.sendMessage(chat_id, 
        f"DataLogger Online\nIP: {get_ip()}\nTemp: {get_temps()}")

# 4. Push Notifications
# Using Pushover, Pushbullet, or ntfy.sh
import requests

def notify_online():
    requests.post("https://ntfy.sh/mydatalogger", 
        data="DataLogger is online",
        headers={"Title": "DataLogger Status"})

# 5. Local Network Discovery
# UDP Broadcast for discovery
import socket

def broadcast_presence():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    message = f"DATALOGGER:{get_ip()}:{get_mac()}"
    sock.sendto(message.encode(), ('<broadcast>', 9999))
```

## 7. Email Notification System

### Email Configuration:
```python
# Using SMTP
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailNotifier:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender = "datalogger@gmail.com"
        self.password = "app_specific_password"
        
    def send_alert(self, subject, body, recipients):
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = self.sender
        msg['To'] = ', '.join(recipients)
        msg.attach(MIMEText(body, 'html'))
        
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.sender, self.password)
            server.send_message(msg)

# Alert Conditions:
alerts = {
    'high_temp': {'threshold': 80, 'channels': [1,2,3]},
    'low_temp': {'threshold': 10, 'channels': [1,2,3]},
    'sensor_failure': {'consecutive_errors': 5},
    'disk_full': {'threshold': 90},  # percentage
    'network_loss': {'timeout': 300}  # seconds
}

# Scheduled Reports:
# Daily summary at 8 AM
# Weekly report on Monday
# Monthly report on 1st
```

## 8. Remote Power Control

### A. Software Reboot/Shutdown:
```python
# Web API endpoints
@app.route('/api/system/reboot', methods=['POST'])
def system_reboot():
    # Verify authentication
    # Save current state
    # Graceful shutdown
    os.system('sudo reboot')

@app.route('/api/system/shutdown', methods=['POST'])
def system_shutdown():
    os.system('sudo shutdown -h now')

# Schedule power cycles
@app.route('/api/system/schedule', methods=['POST'])
def schedule_power():
    # Use cron for scheduling
    # Options: reboot, shutdown, start logging, stop logging
    pass
```

### B. Wake-on-LAN (WoL):
```bash
# Enable WoL (if ethernet connected)
sudo ethtool -s eth0 wol g

# Wake from another device:
wakeonlan MAC_ADDRESS
```

### C. Smart Plug Integration:
```python
# Control via smart plugs (Tasmota, TP-Link Kasa, etc.)
import requests

class SmartPlugController:
    def __init__(self, plug_ip):
        self.plug_ip = plug_ip
        
    def power_on(self):
        requests.get(f"http://{self.plug_ip}/cm?cmnd=Power%20On")
        
    def power_off(self):
        requests.get(f"http://{self.plug_ip}/cm?cmnd=Power%20Off")
        
    def power_cycle(self):
        self.power_off()
        time.sleep(5)
        self.power_on()
```

### D. Hardware Solutions:
```
1. PiJuice HAT - UPS and power management
   - Remote power on/off
   - Battery backup
   - Scheduled power cycles
   
2. Witty Pi - RTC and power management
   - Scheduled on/off times
   - Power cut recovery
   
3. Custom relay board
   - GPIO controlled relay
   - External power control
   
4. PoE HAT (Power over Ethernet)
   - Remote power control via PoE switch
```

### E. Remote Management Tools:
```bash
# 1. VPN Access (WireGuard/OpenVPN)
sudo apt-get install wireguard
# Configure for remote access

# 2. Reverse SSH Tunnel
ssh -R 2222:localhost:22 user@public-server

# 3. TeamViewer for Raspberry Pi
# Download ARM version

# 4. RealVNC
sudo apt-get install realvnc-vnc-server

# 5. Dataplicity
# Cloud service for remote access
curl -s https://www.dataplicity.com/install.sh | sudo bash
```

## Implementation Priority:

### Phase 1 (Essential):
1. Text file storage
2. CSV download from text files
3. Email notifications for alerts
4. Basic GPIO buttons (start/stop/shutdown)

### Phase 2 (Enhanced):
1. Improved graphs (Plotly.js)
2. WiFi AP mode for configuration
3. Online status monitoring (heartbeat)
4. Scheduled email reports

### Phase 3 (Advanced):
1. Bluetooth connectivity
2. Mobile app development
3. Smart plug integration
4. Remote power management

## Security Considerations:
- API authentication (JWT tokens)
- HTTPS for web interface
- Encrypted storage for credentials
- Rate limiting for API endpoints
- Firewall configuration
- VPN for remote access

## Resource Requirements:
- Additional Python packages: plotly, flask-jwt, bluetooth, schedule
- System packages: hostapd, dnsmasq, avahi-daemon
- Hardware: GPIO buttons, LEDs, (optional) OLED display
- Network: Static IP or DDNS for remote access