# DataLogger Project Structure

> **Last Updated:** 2025-10-01 (Cleaned & Organized)

## 📂 Project Organization

```
DataLogger/
│
├── 📁 data-logger-project/          # Main application code
│   ├── app.py                       # ✅ Simple Flask API server
│   ├── app_pi5_final.py            # ✅ Production Pi5 application
│   ├── data_logger.py              # ✅ Core logging functionality (FIXED)
│   ├── database.py                 # ✅ SQLite operations (FIXED)
│   ├── database_manager.py         # Advanced database operations
│   ├── calibration.py              # Temperature calibration
│   ├── config.py                   # Configuration management
│   ├── gpio_controller.py          # GPIO/relay control
│   ├── notification_system.py      # Email/SMS notifications
│   ├── storage_manager.py          # USB/SD card storage
│   ├── telegram_bot.py             # Telegram bot integration
│   ├── text_file_logger.py         # Text file logging
│   ├── wsgi.py                     # WSGI entry point
│   │
│   ├── config.json                 # Application configuration
│   ├── calibration.json            # Calibration factors
│   ├── requirements.txt            # Python dependencies
│   │
│   ├── 📁 sm_tc/                   # Sequent Microsystems HAT driver
│   │   └── __init__.py             # I2C communication + mock mode
│   │
│   ├── 📁 templates/               # Web interface HTML
│   │   ├── dashboard.html          # ✅ Modern dashboard (FIXED)
│   │   └── index.html              # ✅ Classic interface (FIXED)
│   │
│   ├── 📁 static/                  # Web assets
│   │   ├── js/
│   │   │   └── app.js              # ✅ Dashboard JavaScript (FIXED)
│   │   └── README_LOGO.md
│   │
│   └── 📁 data/                    # Data storage (gitignored)
│       ├── raw/                    # Raw sensor data
│       ├── daily/                  # Consolidated daily files
│       └── compressed/             # Archived data
│
├── 📁 testing/                      # ✅ Test scripts (ORGANIZED)
│   ├── test_daq.py                 # Hardware connection tests
│   ├── test_connection.py          # Connection tests
│   ├── test_telegram_connection.py # Telegram bot tests
│   ├── test_gpio.py                # GPIO tests
│   ├── ping_test.py                # Network ping tests
│   ├── test_bot_simple.py          # Simple bot test
│   └── quick_bot_test.py           # Quick bot test
│
├── 📁 network_testing/              # Network connectivity testing
│   ├── test_all_methods.py         # Automated network tests
│   ├── generate_pdf_report.py      # PDF checklist generator
│   └── network_testing_checklist.html
│
├── 📁 documentation/                # Project documentation
│   ├── GPIO_HARDWARE_GUIDE.txt     # GPIO setup guide
│   ├── GPIO_SHOPPING_LIST.md       # Hardware shopping list
│   ├── GPIO_WIRING_DIAGRAM.md      # Wiring diagrams
│   ├── PI5_DEPLOYMENT_FINAL.md     # Deployment guide
│   ├── TELEGRAM_BOT_SETUP.md       # Telegram setup
│   └── README.md                   # Documentation index
│
├── 📁 hardware/                     # Hardware deployment scripts
│   ├── install.sh                  # Hardware installation
│   ├── launch_datalogger.sh        # Launch script
│   └── README.md                   # Hardware setup guide
│
├── 📄 CLAUDE.md                     # ✅ AI assistant instructions
├── 📄 README.md                     # Project overview
├── 📄 PROJECT_STRUCTURE.md          # This file
├── 📄 NETWORK_TESTING_CHECKLIST.md  # Network testing guide
├── 🔧 pi5_setup_v2.sh               # ✅ Automated Pi5 setup
├── .gitignore                       # ✅ Git ignore rules (UPDATED)
└── .git/                            # Git repository
```

---

## 🎯 Quick Reference

### Core Application Files

| File | Purpose | Status |
|------|---------|--------|
| `app.py` | Simple Flask API server | ✅ Working |
| `app_pi5_final.py` | Production Pi5 application | ✅ Production |
| `data_logger.py` | Core temperature logging | ✅ Fixed |
| `database.py` | SQLite database operations | ✅ Fixed |
| `templates/dashboard.html` | Modern web dashboard | ✅ Fixed |
| `templates/index.html` | Classic web interface | ✅ Fixed |
| `static/js/app.js` | Dashboard JavaScript | ✅ Fixed |

### Recent Fixes Applied (2025-10-01)

✅ **Critical Fixes:**
- Fixed missing return statement in `database.py` → Data export now works
- Fixed API response parsing in `dashboard.html` → GUI controls now respond
- Fixed sensor toggle parameters → Channel enable/disable works
- Fixed `is_connected()` function → Proper connection status
- Moved Flask imports to module level → Better performance

✅ **Code Organization:**
- Removed duplicate app files (app_enhanced.py, app_pi5_ready.py)
- Moved test files to `/testing` directory
- Removed old backup ZIP (300KB saved)
- Removed duplicate folders (development/, production/)
- Updated .gitignore with comprehensive rules

---

## 🚀 Quick Start

### On Raspberry Pi 5

```bash
# Initial setup
cd /home/pi/DataLogger
sudo bash pi5_setup_v2.sh

# Run production application
python3 data-logger-project/app_pi5_final.py

# Or run as system service
sudo systemctl start datalogger
sudo systemctl status datalogger
```

### Development/Testing (Windows/Mac/Linux)

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r data-logger-project/requirements.txt

# Run simple app (uses mock hardware)
python data-logger-project/app.py

# Access dashboard
# http://localhost:8080
```

---

## 🧪 Testing

### Hardware Tests
```bash
# Test DAQ board connection
python testing/test_daq.py

# Test GPIO
python testing/test_gpio.py
```

### Network Tests
```bash
# Run all network connectivity tests
python network_testing/test_all_methods.py

# Generate PDF checklist
python network_testing/generate_pdf_report.py
```

### Telegram Bot Tests
```bash
# Test Telegram bot connection
python testing/test_telegram_connection.py

# Quick bot test
python testing/quick_bot_test.py
```

---

## 📦 Dependencies

Main Python packages (see `requirements.txt`):
- **Flask** - Web server
- **gunicorn** - Production WSGI server
- **smbus2** - I2C communication
- **python-telegram-bot** - Telegram integration
- **RPi.GPIO** - Raspberry Pi GPIO control

---

## 🗂️ File Purposes

### Main Application
- **app.py** - Basic Flask server, good for development/testing
- **app_pi5_final.py** - Production version with all features enabled

### Core Modules
- **data_logger.py** - Handles sensor reading, threading, intervals
- **database.py** - Basic SQLite operations (latest, historical, averages)
- **database_manager.py** - Advanced DB operations, backup, export
- **calibration.py** - Temperature correction factors (JSON-based)
- **config.py** - Configuration file management

### Features
- **gpio_controller.py** - Control relays/LEDs via GPIO pins
- **notification_system.py** - Email/SMS alerts for critical events
- **telegram_bot.py** - Telegram bot for remote monitoring
- **storage_manager.py** - USB/SD card data export
- **text_file_logger.py** - Backup logging to text files

### Hardware
- **sm_tc/\_\_init\_\_.py** - Sequent Microsystems 8-Thermocouple HAT driver
  - Real I2C implementation for Raspberry Pi
  - Mock implementation for Windows/Mac development

---

## 🔒 Ignored Files (.gitignore)

The following are NOT tracked in Git:
- `*.db` - SQLite databases
- `*.log` - Log files
- `data/raw/*.txt` - Raw sensor data
- `__pycache__/` - Python cache
- `simulated_*/` - Temporary test folders
- `.env` - Environment variables

---

## 📝 Notes

1. **Production File**: Use `app_pi5_final.py` for deployment on Raspberry Pi 5
2. **Mock Hardware**: Development on Windows/Mac uses simulated sensor data
3. **Database**: SQLite file `datalogger.db` is auto-created on first run
4. **Web Interfaces**:
   - Dashboard (modern): http://localhost:8080/
   - Classic: http://localhost:8080/classic

---

## 🐛 Known Issues & Solutions

### Issue: Board won't connect
**Solution:** Check I2C is enabled: `sudo raspi-config` → Interface Options → I2C

### Issue: Permission denied on GPIO
**Solution:** Run with sudo or add user to gpio group: `sudo usermod -a -G gpio $USER`

### Issue: Database locked
**Solution:** Close all connections, check for multiple instances running

---

## 📞 Support

- **Documentation**: See `/documentation` folder
- **Hardware Setup**: See `hardware/README.md`
- **Network Issues**: See `NETWORK_TESTING_CHECKLIST.md`
- **Telegram Bot**: See `documentation/TELEGRAM_BOT_SETUP.md`

---

**Project Status:** ✅ Clean, Organized, and Fully Functional
**Last Code Review:** 2025-10-01
