# 🌡️ DataLogger - Professional Temperature Monitoring System

Complete Raspberry Pi 5 temperature data logging system with 8-channel thermocouple support, Telegram bot integration, web dashboard, and optional GPIO control.

## 🆕 Latest Updates (December 2024)
- ✅ Fixed DAQ connection handling - no phantom readings before connection
- ✅ Added Telegram bot connect/disconnect commands
- ✅ Improved connection status display in web interface
- ✅ Enhanced error handling for disconnected state
- ✅ Added connection validation before operations

## 📁 **ORGANIZED PROJECT STRUCTURE**

### 🚀 **[production/](production/)** - Ready for Pi5 Deployment
- `app_pi5_final.py` - **MAIN APPLICATION** (tested & working)
- Complete production-ready system
- Use this for Pi5 deployment

### 🔧 **[development/](development/)** - Development Versions  
- `app_enhanced.py` - Enhanced development version
- `app_pi5_ready.py` - Pi5 compatibility testing version
- Development and testing files

### 🧪 **[testing/](testing/)** - Test Scripts
- `test_telegram_bot.py` - Telegram bot tests
- `quick_bot_test.py` - Quick bot validation
- `test_gpio.py` - GPIO hardware tests

### 📚 **[documentation/](documentation/)** - Setup Guides
- `PI5_DEPLOYMENT_FINAL.md` - **COMPLETE PI5 SETUP GUIDE**
- `TELEGRAM_BOT_SETUP.md` - Telegram bot setup
- Hardware wiring and shopping guides

### ⚡ **[hardware/](hardware/)** - GPIO & Physical Components
- `gpio_controller.py` - Physical button/LED control
- System service files
- Installation scripts

### 🗂️ **[data-logger-project/](data-logger-project/)** - Core System Files
- All supporting modules and dependencies
- Database, configuration, and utility files
- Templates and static files for web interface

---

## 🚀 **QUICK START - Pi5 Deployment**

### Step 1: Clone Repository
```bash
cd ~/
git clone https://github.com/eengrajesh/DataLogger.git
cd DataLogger
```

### Step 2: Install Dependencies  
```bash
pip install -r data-logger-project/requirements.txt --break-system-packages
```

### Step 3: Configure System
```bash
# Edit configuration
cd data-logger-project
nano config.json  # Add your Telegram bot token and user ID
```

### Step 4: Run Application
```bash
python app.py
```

### Step 5: Access Your System
- **Web Dashboard**: http://your-pi-ip:8080
- **Telegram Bot**: Your configured bot
- Connect to DAQ: Click "Connect" button or use `/connect` in Telegram

---

## ✅ **WHAT'S INCLUDED**

### 📱 **Remote Control via Telegram**
- Monitor temperatures from anywhere globally  
- Connect/disconnect DAQ board remotely
- Start/stop logging remotely via any device
- Get real-time alerts and notifications
- Download data files instantly
- Complete system control with inline buttons

### 🌐 **Professional Web Dashboard**
- Real-time temperature graphs for 8 channels
- Historical data visualization  
- DAQ connection management
- System monitoring and control
- Mobile-responsive design
- Data export functionality (CSV/JSON)
- Per-channel calibration and intervals

### 🔘 **Optional Physical Control**
- GPIO buttons for local operation
- Status LEDs for visual feedback
- Emergency shutdown capability  
- Works without network connection

### 🛠️ **Production Features**
- SQLite database logging
- Email notification system
- Robust error handling
- Cross-platform compatibility
- System service integration

---

## 📞 **SUPPORT & DOCUMENTATION**

### 📚 Quick Reference
- **Complete Setup**: Read `documentation/PI5_DEPLOYMENT_FINAL.md`
- **Telegram Setup**: Follow `documentation/TELEGRAM_BOT_SETUP.md`  
- **Hardware Guide**: Check `documentation/GPIO_HARDWARE_GUIDE.txt`
- **Testing**: Use scripts in `testing/` folder

### 🤖 Telegram Bot Commands
```
/start - Initialize bot and show menu
/connect - Connect to DAQ board
/disconnect - Disconnect from DAQ board  
/status - System status overview
/temps - Current temperature readings
/logging start/stop - Control data logging
/export 1h/24h/7d - Export data
/help - Show all commands
```

### 🔧 Troubleshooting

**Issue: Temperature shows "--.-°C" in web interface**
- Solution: Click "Connect" button to connect to DAQ board

**Issue: Cannot start logging**
- Solution: Ensure DAQ is connected first

**Issue: Telegram bot not responding**
- Solution: Check bot token and user ID in config.json

**Issue: I2C communication error on Pi5**
- Solution: Enable I2C with `sudo raspi-config` and check connections

---

## 🏆 **SYSTEM SPECIFICATIONS**

### Hardware Support
- **DAQ Board**: Sequent Microsystems 8-Thermocouple HAT
- **Sensors**: K-type thermocouples (supports B,E,J,K,N,R,S,T types)
- **Channels**: 8 independent temperature channels
- **Platform**: Raspberry Pi 5 (also works on Pi 3/4)
- **Communication**: I2C interface

### Software Features
- **Database**: SQLite with automatic maintenance
- **Web Server**: Flask with RESTful API
- **Real-time Updates**: 5-second default interval (configurable per channel)
- **Data Export**: CSV and JSON formats
- **Calibration**: Per-channel offset correction
- **Multi-threading**: Background logging with proper synchronization

## ✅ **DEVELOPMENT STATUS**

**FULLY TESTED & PRODUCTION READY**
- ✅ Pi5 compatibility verified
- ✅ Connection handling fixed
- ✅ Telegram bot enhanced
- ✅ Web interface improved
- ✅ Error handling strengthened

---

Your complete professional DataLogger with global remote access is ready! 🌍