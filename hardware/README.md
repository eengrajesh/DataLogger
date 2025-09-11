# ⚡ HARDWARE - GPIO & Physical Components

## Hardware Files
- **`gpio_controller.py`** - GPIO button and LED control
- **`datalogger.service`** - System service file
- **`datalogger.desktop`** - Desktop shortcut file
- **`install.sh`** - Installation script
- **`launch_datalogger.sh`** - Launch script

## GPIO Components
- Physical buttons for start/stop
- Status LEDs for system feedback  
- Emergency shutdown capability
- Pi5 GPIO pin connections

## Installation
```bash
cd DataLogger/hardware
chmod +x install.sh
sudo ./install.sh
```

## Service Management
```bash
sudo systemctl enable datalogger
sudo systemctl start datalogger
sudo systemctl status datalogger
```

## Notes
Hardware components are optional. The system works without physical GPIO components using web and Telegram interfaces.