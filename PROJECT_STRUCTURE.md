# DataLogger Project File Organization

## Current Project Structure

```
DataLogger/
│
├── 📁 data-logger-project/          # Main application code
│   ├── app.py                       # Basic Flask API server
│   ├── app_pi5_final.py            # Production-ready Pi5 application
│   ├── data_logger.py              # Core data logging functionality
│   ├── database.py                 # SQLite database operations
│   ├── calibration.py              # Temperature calibration
│   ├── telegram_bot.py             # Telegram bot integration
│   ├── gpio_controller.py          # GPIO control for relays
│   ├── notification_system.py      # Email/SMS notifications
│   ├── storage_manager.py          # USB/SD card storage
│   ├── database_manager.py         # Advanced database operations
│   ├── config.py                   # Configuration management
│   ├── requirements.txt            # Python dependencies
│   │
│   ├── 📁 sm_tc/                   # Sequent Microsystems HAT driver
│   │   └── __init__.py             # I2C communication & mock mode
│   │
│   ├── 📁 templates/               # Web interface HTML
│   │   └── index.html              # Main dashboard
│   │
│   ├── 📁 static/                  # Web assets
│   │   ├── css/                   # Stylesheets
│   │   └── js/                    # JavaScript files
│   │
│   └── 📁 data/                    # Data storage
│       └── datalogger.db           # SQLite database
│
├── 📁 network_testing/              # Network connectivity testing
│   ├── test_all_methods.py         # Automated network tests
│   ├── generate_pdf_report.py      # PDF checklist generator
│   ├── network_testing_checklist.html
│   └── network_testing_checklist.pdf
│
├── 📁 development/                  # Development versions
│   └── (development scripts)
│
├── 📁 production/                   # Production deployments
│   └── (production configs)
│
├── 📁 testing/                      # Test scripts
│   ├── test_daq.py                # Hardware tests
│   ├── test_connection.py         # Connection tests
│   └── ping_test.py               # Network tests
│
├── 📁 documentation/                # Project documentation
│   └── (user manuals, API docs)
│
├── 📁 hardware/                     # Hardware schematics
│   └── (wiring diagrams, datasheets)
│
├── 📦 DataLogger_Backup_2025-01-16.zip  # Full backup
├── 📄 README.md                     # Project overview
├── 📄 CLAUDE.md                     # AI assistant instructions
├── 📄 NETWORK_TESTING_CHECKLIST.md  # Printable checklist
├── 🔧 pi5_setup.sh                  # Automated Pi5 setup script
├── .gitignore                       # Git ignore rules
└── .git/                            # Git repository

```

## File Categories

### 🎯 Core Application Files
- `app_pi5_final.py` - **MAIN PRODUCTION FILE** (Use this on Pi5)
- `data_logger.py` - Temperature reading logic
- `database.py` - Data storage
- `sm_tc/__init__.py` - Hardware communication

### 🌐 Network Testing Files
- `network_testing/test_all_methods.py` - Run all connectivity tests
- `network_testing/network_testing_checklist.pdf` - Print this for manual testing
- `NETWORK_TESTING_CHECKLIST.md` - Digital reference

### 🔧 Configuration Files
- `config.json` - Application settings
- `calibration.json` - Temperature corrections
- `requirements.txt` - Python packages

### 📊 Web Interface
- `templates/index.html` - Dashboard UI
- `static/` - CSS/JS assets

### 🤖 Automation & Integration
- `telegram_bot.py` - Telegram notifications
- `notification_system.py` - Email/SMS alerts
- `gpio_controller.py` - Relay control

## Quick Start Commands

### On Raspberry Pi 5:
```bash
# Initial setup
cd /home/pi/DataLogger
sudo bash pi5_setup.sh

# Run main application
python3 data-logger-project/app_pi5_final.py

# Or as a service
sudo systemctl start datalogger
sudo systemctl status datalogger
```

### Network Testing:
```bash
# Run automated tests
python3 network_testing/test_all_methods.py

# Generate PDF checklist
python3 network_testing/generate_pdf_report.py
```

### Development Testing:
```bash
# Test hardware connection
python3 data-logger-project/test_daq.py

# Test Telegram bot
python3 data-logger-project/test_telegram_connection.py
```

## Important Notes

1. **Main Application**: Use `app_pi5_final.py` for production
2. **Backup Created**: `DataLogger_Backup_2025-01-16.zip` contains all files before network testing additions
3. **Network Testing**: Complete suite in `network_testing/` folder
4. **Database**: SQLite file `datalogger.db` is gitignored (not in repo)

## Next Steps

1. Print the network testing checklist (PDF)
2. Run `test_all_methods.py` to test each connectivity method
3. Choose the best method(s) for your secured network
4. Configure the selected method(s) in `app_pi5_final.py`