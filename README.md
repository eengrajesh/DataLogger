# 🌡️ DataLogger - Professional Temperature Monitoring System

Complete Raspberry Pi 5 temperature data logging system with Telegram bot integration, web dashboard, and optional GPIO control.

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

### Step 3: Run Production Application
```bash
cd production
cp ../data-logger-project/*.py .
cp -r ../data-logger-project/templates .
cp -r ../data-logger-project/sm_tc .
python app_pi5_final.py
```

### Step 4: Access Your System
- **Telegram Bot**: @eeng_datalogger_bot
- **Web Dashboard**: http://your-pi-ip:8080
- **Your User ID**: 6921883539 (pre-configured)

---

## ✅ **WHAT'S INCLUDED**

### 📱 **Remote Control via Telegram**
- Monitor temperatures from anywhere globally  
- Start/stop logging remotely via iPhone
- Get real-time alerts and notifications
- Download data files instantly
- Complete system control

### 🌐 **Professional Web Dashboard**
- Real-time temperature graphs
- Historical data visualization  
- System monitoring and control
- Mobile-responsive design
- Data export functionality

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

- **Complete Setup**: Read `documentation/PI5_DEPLOYMENT_FINAL.md`
- **Telegram Setup**: Follow `documentation/TELEGRAM_BOT_SETUP.md`  
- **Hardware Guide**: Check `documentation/GPIO_HARDWARE_GUIDE.txt`
- **Testing**: Use scripts in `testing/` folder

---

## 🏆 **DEVELOPMENT STATUS**

✅ **FULLY TESTED & WORKING**
- Development board testing completed
- All functionality verified
- Pi5 compatibility confirmed
- Ready for production deployment

---

Your complete professional DataLogger with global remote access is ready! 🌍