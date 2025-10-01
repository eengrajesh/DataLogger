# 🖱️ Double-Click Setup for Raspberry Pi 5

This guide will help you set up DataLogger to run with a simple double-click on your Raspberry Pi 5.

## ✅ One-Time Setup (Do this once)

### Step 1: Open Terminal on your Pi5

### Step 2: Navigate to the DataLogger folder
```bash
cd ~/DataLogger
```

### Step 3: Run the installer
```bash
bash INSTALL_DESKTOP_ICON.sh
```

That's it! ✅

---

## 🚀 How to Use

### Method 1: Desktop Icon (Easiest)
1. **Double-click** the "DataLogger" icon on your Desktop
2. Browser will open automatically to the dashboard
3. Start logging!

### Method 2: Applications Menu
1. Click Applications Menu
2. Find "DataLogger"
3. Click to launch

---

## 🎯 What Happens When You Launch

1. ✅ Application starts in background
2. ✅ Browser opens to http://localhost:8080
3. ✅ Dashboard is ready to use
4. ✅ All sensors ready to connect

---

## 🛑 How to Stop DataLogger

### Option 1: From Terminal
```bash
pkill -f app_pi5_final.py
```

### Option 2: Restart Pi
The application will stop when you reboot.

---

## 🔧 Advanced: Auto-Start on Boot

If you want DataLogger to start automatically when Pi5 boots:

```bash
# Edit crontab
crontab -e

# Add this line at the end:
@reboot /home/pi/DataLogger/data-logger-project/start_datalogger.sh
```

---

## 📁 Files Created

- **DataLogger.desktop** - Desktop launcher icon
- **data-logger-project/start_datalogger.sh** - Startup script
- **INSTALL_DESKTOP_ICON.sh** - One-time setup installer

---

## 🐛 Troubleshooting

### Issue: Icon doesn't work
**Solution:**
```bash
cd ~/DataLogger
chmod +x data-logger-project/start_datalogger.sh
chmod +x ~/Desktop/DataLogger.desktop
```

### Issue: Browser doesn't open
**Solution:** Open manually: http://localhost:8080

### Issue: Application won't start
**Solution:** Check logs:
```bash
cat /tmp/datalogger.log
```

---

## 📱 Access from Other Devices

Once running, you can access the dashboard from:
- **Same Pi5:** http://localhost:8080
- **Other devices on network:** http://PI5_IP_ADDRESS:8080

To find Pi5 IP address:
```bash
hostname -I
```

---

## ✨ Features

- 🖱️ **Double-click to start** - No terminal needed
- 🌐 **Auto-open browser** - Dashboard ready instantly
- 🔄 **Background running** - Works even after closing browser
- 📊 **Two interfaces** - Modern dashboard + Classic view
- 🛑 **Easy to stop** - Simple kill command

---

**Enjoy your DataLogger! 🌡️📊**
