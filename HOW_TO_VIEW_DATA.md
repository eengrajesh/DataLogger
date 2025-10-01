# 🔍 How to View Your Data

You have **multiple ways** to view your DataLogger data - **NO SQLite installation required!**

---

## Method 1: 🌐 Web Dashboard (Easiest!)

### Just open your browser:
```
http://localhost:8080
```

**Features:**
- ✅ Real-time charts and graphs
- ✅ Historical data visualization
- ✅ Download CSV/JSON directly
- ✅ Beautiful interface
- ✅ **No installation needed!**

**This is the recommended way** - everything is already built-in!

---

## Method 2: 🐍 Python Viewer Script (I just created this!)

### Run the viewer script:
```bash
cd ~/DataLogger/data-logger-project
python3 view_data.py
```

**What you'll see:**
```
📊 DATALOGGER - DATA VIEWER
=====================================

1. View Database Statistics
2. Export Database to CSV
3. View Text Files Info
4. Exit

Select option (1-4):
```

**Features:**
- ✅ View total records
- ✅ See per-channel statistics
- ✅ View latest 20 readings
- ✅ Export to CSV file
- ✅ See text file information
- ✅ **No SQLite browser needed!**

---

## Method 3: 📄 Text Files (Direct Access)

Your data is also saved as plain text files!

### View raw data files:
```bash
# See today's data
cat ~/DataLogger/data-logger-project/data/raw/2025-10-01_14.txt

# See daily consolidated file
cat ~/DataLogger/data-logger-project/data/daily/2025-10-01.txt
```

**Format:**
```
timestamp,channel,raw_temp,calibrated_temp
2025-10-01 14:23:45,1,25.3,25.3
2025-10-01 14:23:45,2,26.1,26.1
```

**Features:**
- ✅ Plain text CSV format
- ✅ Can open with Excel, LibreOffice
- ✅ No special software needed
- ✅ Easy to backup/share

---

## Method 4: 💻 Python Code (For Programmers)

If you want to access data programmatically:

```python
# Simple example
from database import get_all_data, get_latest_readings

# Get latest readings for each channel
latest = get_latest_readings()
for reading in latest:
    print(f"CH{reading['thermocouple_id']}: {reading['temperature']}°C")

# Get all historical data
all_data = get_all_data()
print(f"Total records: {len(all_data)}")
```

---

## Method 5: 🖥️ SQLite Browser (Optional - If You Want GUI)

**Only if you want a database GUI tool:**

### On Raspberry Pi:
```bash
# Install SQLite Browser (one time)
sudo apt install sqlitebrowser

# Open your database
sqlitebrowser ~/DataLogger/data-logger-project/datalogger.db
```

**But this is optional!** The web dashboard is easier and better.

---

## Quick Comparison:

| Method | Installation Required? | Best For |
|--------|----------------------|----------|
| **Web Dashboard** | ❌ No | ⭐ **Recommended** - Charts, graphs, everything! |
| **Python Viewer** | ❌ No | Quick stats and CSV export |
| **Text Files** | ❌ No | Direct file access, Excel export |
| **Python Code** | ❌ No | Custom programming/analysis |
| **SQLite Browser** | ✅ Yes | Advanced database queries |

---

## 📊 Quick Start Guide

### 1. Start DataLogger:
```bash
# Double-click the Desktop icon, OR:
cd ~/DataLogger/data-logger-project
bash start_datalogger.sh
```

### 2. View Data:
```bash
# Option A: Open browser (automatic)
# http://localhost:8080

# Option B: Run viewer script
python3 view_data.py

# Option C: View text files
cat data/daily/$(date +%Y-%m-%d).txt
```

---

## 📤 Export Your Data

### From Web Dashboard:
1. Open http://localhost:8080
2. Go to "Data Export" section
3. Select date range
4. Click "CSV Export" or "JSON"

### Using Python Viewer:
```bash
python3 view_data.py
# Select option 2: Export Database to CSV
```

### Copy Text Files:
```bash
# Copy all data to USB drive
cp -r data/ /media/usb/backup/
```

---

## 🎯 Summary

**You DON'T need to install SQLite!**

Everything you need is already included:
- ✅ Web dashboard (built-in)
- ✅ Python viewer script (just created!)
- ✅ Text files (always there)

**Best way:** Just use the web dashboard at http://localhost:8080 🌐

---

**Enjoy viewing your data!** 📊✨
