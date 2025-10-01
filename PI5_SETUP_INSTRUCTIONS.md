# 🚀 Complete Pi5 Setup Instructions

## Step-by-Step Guide to Get All Updates on Your Raspberry Pi 5

Follow these steps **in order** to get your DataLogger fully updated and running with all new features!

---

## 📋 Prerequisites

Before you start, make sure you have:
- ✅ Raspberry Pi 5 powered on
- ✅ Internet connection
- ✅ Keyboard and monitor (or SSH access)
- ✅ Terminal window open

---

## 🔧 Step 1: Update Pi5 System (Optional but Recommended)

```bash
# Update package lists
sudo apt update

# Upgrade installed packages (takes 5-10 minutes)
sudo apt upgrade -y

# Clean up
sudo apt autoremove -y
```

**Why?** Ensures your Pi5 has latest security updates and bug fixes.

---

## 📥 Step 2: Navigate to DataLogger Project

```bash
# Go to home directory
cd ~

# If DataLogger folder already exists:
cd DataLogger

# If NOT yet cloned, clone from GitHub:
# git clone https://github.com/eengrajesh/DataLogger.git
# cd DataLogger
```

---

## 🔄 Step 3: Pull Latest Changes from GitHub

```bash
# Make sure you're in the DataLogger directory
cd ~/DataLogger

# Pull all latest updates
git pull origin main
```

**You should see:**
```
remote: Counting objects...
Unpacking objects: 100% done.
From https://github.com/eengrajesh/DataLogger
 * branch            main       -> FETCH_HEAD
Updating 4bf4d95..1e1101a
Fast-forward
 [list of updated files]
```

---

## 📦 Step 4: Install/Update Python Dependencies

```bash
# Navigate to project folder
cd ~/DataLogger/data-logger-project

# Create virtual environment (if not exists)
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

**You should see:**
```
Successfully installed Flask-X.X.X gunicorn-X.X.X ...
```

---

## 🖱️ Step 5: Install Desktop Icon for Double-Click Launch

```bash
# Go back to main directory
cd ~/DataLogger

# Make installer executable
chmod +x INSTALL_DESKTOP_ICON.sh

# Run the installer
bash INSTALL_DESKTOP_ICON.sh
```

**You should see:**
```
==========================================
  DataLogger Desktop Icon Installer
==========================================

✅ Installation Complete!

You can now:
  1. Double-click 'DataLogger' icon on Desktop
  2. Find 'DataLogger' in Applications menu
```

---

## 🗄️ Step 6: Install SQLite Browser (Optional)

```bash
# Update package list
sudo apt update

# Install SQLite Browser
sudo apt install sqlitebrowser -y
```

**Installation size:** ~15 MB
**Time:** ~1-2 minutes

---

## ✅ Step 7: Verify Installation

### Check Files Are Updated:

```bash
cd ~/DataLogger

# List new files (should see these):
ls -1

# You should see:
# - DOUBLE_CLICK_SETUP.md
# - DATA_STORAGE_GUIDE.md
# - HOW_TO_VIEW_DATA.md
# - SQLITE_BROWSER_SETUP.md
# - DataLogger.desktop
# - INSTALL_DESKTOP_ICON.sh
# - PI5_SETUP_INSTRUCTIONS.md (this file)
```

### Check Desktop Icon:

```bash
# Check Desktop icon exists
ls -l ~/Desktop/DataLogger.desktop

# Should show:
# -rwxr-xr-x 1 pi pi ... DataLogger.desktop
```

---

## 🚀 Step 8: Test the Application

### Option 1: Double-Click Desktop Icon
1. Go to Desktop
2. Find **"DataLogger"** icon
3. **Double-click** it
4. Browser should open automatically to http://localhost:8080

### Option 2: Manual Launch (for testing)
```bash
cd ~/DataLogger/data-logger-project

# Run the app
python3 app_pi5_final.py
```

**You should see:**
```
 * Running on http://0.0.0.0:8080
 * Running on http://192.168.1.X:8080
Press CTRL+C to quit
```

### Test in Browser:
1. Open browser on Pi5
2. Go to: `http://localhost:8080`
3. You should see the DataLogger dashboard

---

## 🧪 Step 9: Test All New Features

### Test 1: Double-Click Launcher
```bash
# From desktop, double-click DataLogger icon
# ✅ Should start app and open browser
```

### Test 2: Python Data Viewer
```bash
cd ~/DataLogger/data-logger-project
python3 view_data.py

# ✅ Should show interactive menu
```

### Test 3: SQLite Browser (if installed)
```bash
cd ~/DataLogger/data-logger-project
sqlitebrowser datalogger.db

# ✅ Should open database GUI
```

### Test 4: Web Dashboard
```
Open browser: http://localhost:8080

✅ Check these work:
- Connect button
- Disconnect button
- Start Logging button
- Stop Logging button
- Sensor toggles
- Data export
```

---

## 📊 Step 10: Verify All Bug Fixes Are Applied

### Test Fixed Features:

#### 1. Test Data Export (was broken, now fixed)
```
1. Go to http://localhost:8080
2. Click "Download Data" → CSV
3. ✅ Should download file successfully
```

#### 2. Test Board Connection (was broken, now fixed)
```
1. Click "Connect" button
2. ✅ Status should change to "Connected"
3. Click "Disconnect"
4. ✅ Status should change to "Disconnected"
```

#### 3. Test Logging Controls (was broken, now fixed)
```
1. Click "Start Logging"
2. ✅ Status indicator should turn green
3. Click "Stop Logging"
4. ✅ Status indicator should turn red/gray
```

#### 4. Test Sensor Toggles (was broken, now fixed)
```
1. Toggle any sensor channel on/off
2. ✅ Should enable/disable immediately
3. Check that only active sensors show data
```

---

## 🎯 Complete Checklist

Print this and check off as you complete each step:

```
□ Step 1: System update (apt update & upgrade)
□ Step 2: Navigate to DataLogger folder
□ Step 3: Git pull latest changes
□ Step 4: Install Python dependencies
□ Step 5: Install desktop icon
□ Step 6: Install SQLite Browser (optional)
□ Step 7: Verify all files present
□ Step 8: Test application launches
□ Step 9: Test new features work
□ Step 10: Verify bug fixes applied

BONUS:
□ Read DOUBLE_CLICK_SETUP.md
□ Read DATA_STORAGE_GUIDE.md
□ Read HOW_TO_VIEW_DATA.md
□ Read SQLITE_BROWSER_SETUP.md
```

---

## 📁 New Files You Now Have

After completing all steps, you'll have these **new files**:

### Documentation:
- ✅ `DOUBLE_CLICK_SETUP.md` - How to use desktop launcher
- ✅ `DATA_STORAGE_GUIDE.md` - Complete storage documentation
- ✅ `HOW_TO_VIEW_DATA.md` - Guide to viewing your data
- ✅ `SQLITE_BROWSER_SETUP.md` - SQLite Browser guide
- ✅ `PI5_SETUP_INSTRUCTIONS.md` - This file!
- ✅ `PROJECT_STRUCTURE.md` - Updated project overview

### Launcher Files:
- ✅ `DataLogger.desktop` - Desktop icon definition
- ✅ `INSTALL_DESKTOP_ICON.sh` - Icon installer script
- ✅ `data-logger-project/start_datalogger.sh` - Main launcher
- ✅ `pi5_setup_v2.sh` - System setup script

### Tools:
- ✅ `data-logger-project/view_data.py` - Python data viewer

### Updated Code Files:
- ✅ `data-logger-project/app.py` - Fixed imports
- ✅ `data-logger-project/database.py` - Fixed return statement
- ✅ `data-logger-project/data_logger.py` - Fixed is_connected()
- ✅ `data-logger-project/templates/dashboard.html` - Fixed API calls
- ✅ `.gitignore` - Updated ignore rules

### Removed (Cleaned Up):
- ❌ Old duplicates (app_enhanced.py, app_pi5_ready.py)
- ❌ Old backup ZIP
- ❌ development/ folder
- ❌ production/ folder
- ❌ Old setup script (pi5_setup.sh)

---

## 🐛 Troubleshooting

### Issue: "git pull" shows conflicts

**Solution:**
```bash
# Save your local changes (if any)
git stash

# Pull updates
git pull origin main

# Restore your changes (if needed)
git stash pop
```

### Issue: Desktop icon doesn't appear

**Solution:**
```bash
# Re-run installer
cd ~/DataLogger
bash INSTALL_DESKTOP_ICON.sh

# Or manually copy
cp DataLogger.desktop ~/Desktop/
chmod +x ~/Desktop/DataLogger.desktop
```

### Issue: "pip install" fails

**Solution:**
```bash
# Make sure virtual environment is activated
cd ~/DataLogger/data-logger-project
source .venv/bin/activate

# Try installing one by one
pip install Flask
pip install gunicorn
# etc...
```

### Issue: "python3 not found" or "command not found"

**Solution:**
```bash
# Install Python 3
sudo apt update
sudo apt install python3 python3-pip python3-venv -y
```

### Issue: SQLite Browser won't install

**Solution:**
```bash
# Update package lists
sudo apt update

# Try installing with full name
sudo apt install sqlitebrowser

# Alternative name on some systems
sudo apt install sqlite3
```

### Issue: Application won't start

**Solution:**
```bash
# Check if port 8080 is already in use
sudo lsof -i :8080

# Kill existing process
pkill -f app_pi5_final.py

# Try again
cd ~/DataLogger/data-logger-project
python3 app_pi5_final.py
```

---

## 🔄 Quick Command Summary

**Copy and paste this entire block to do everything:**

```bash
# ============================================
#  DataLogger Pi5 Complete Setup Script
# ============================================

# Navigate to project
cd ~/DataLogger

# Pull latest updates
git pull origin main

# Setup Python environment
cd data-logger-project
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Install desktop icon
cd ~/DataLogger
bash INSTALL_DESKTOP_ICON.sh

# Install SQLite Browser (optional)
sudo apt install sqlitebrowser -y

# Make scripts executable
chmod +x data-logger-project/start_datalogger.sh
chmod +x pi5_setup_v2.sh

echo ""
echo "=========================================="
echo "  ✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Now you can:"
echo "  1. Double-click 'DataLogger' on Desktop"
echo "  2. Or run: cd ~/DataLogger/data-logger-project && python3 app_pi5_final.py"
echo ""
```

---

## 📚 Next Steps After Setup

### 1. Read the Documentation
```bash
# View guides
cat ~/DataLogger/DOUBLE_CLICK_SETUP.md
cat ~/DataLogger/HOW_TO_VIEW_DATA.md
```

### 2. Start Using DataLogger
```
Double-click Desktop icon → Dashboard opens → Start logging!
```

### 3. Connect Your Hardware
- Connect Sequent Microsystems DAQ HAT
- Connect thermocouples to channels 1-8
- Click "Connect" in dashboard

### 4. Start Logging Data
- Click "Start Logging"
- Watch real-time temperatures
- View charts and graphs

---

## 🎯 What's New in This Update?

### 🐛 Bug Fixes:
- ✅ Data export now works (CSV/JSON download)
- ✅ Connect/Disconnect buttons respond correctly
- ✅ Start/Stop logging updates status properly
- ✅ Sensor toggles enable/disable channels correctly
- ✅ Connection status checks work properly

### 🆕 New Features:
- ✅ Double-click desktop launcher
- ✅ Auto-opens browser on startup
- ✅ Python data viewer script
- ✅ Comprehensive documentation

### 🧹 Improvements:
- ✅ Cleaned up duplicate files
- ✅ Organized test files
- ✅ Better project structure
- ✅ Updated .gitignore
- ✅ Optimized imports for better performance

---

## ✅ Success Indicators

**You'll know everything is working when:**

1. ✅ Desktop icon appears and launches app
2. ✅ Browser opens automatically to dashboard
3. ✅ All buttons respond correctly
4. ✅ Data export downloads CSV/JSON
5. ✅ Sensor toggles work
6. ✅ Connection status updates properly
7. ✅ Python viewer shows data
8. ✅ SQLite Browser opens database (if installed)

---

## 📞 Support

If you encounter any issues:

1. Check **Troubleshooting** section above
2. Review documentation files
3. Check GitHub Issues: https://github.com/eengrajesh/DataLogger/issues
4. All fixes are documented in `PROJECT_STRUCTURE.md`

---

## 🎉 Congratulations!

Once you complete all steps, your Pi5 will have:
- ✅ Latest bug fixes
- ✅ New features
- ✅ Clean project structure
- ✅ Easy double-click launch
- ✅ Professional data viewing tools
- ✅ Complete documentation

**Enjoy your upgraded DataLogger!** 🌡️📊

---

**Last Updated:** 2025-10-01
**Version:** 2.0 (Major Update)
