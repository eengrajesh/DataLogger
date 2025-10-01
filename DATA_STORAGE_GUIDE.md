# 📊 Data Storage Guide - DataLogger

## Overview

Your DataLogger uses **TWO parallel storage systems** for redundancy and flexibility:

1. **SQLite Database** - Fast queries, web dashboard
2. **Text Files** - Long-term backup, easy export

---

## 1️⃣ SQLite Database (Primary Storage)

### Location
```
data-logger-project/datalogger.db
```

### Database Schema
```sql
readings table:
├── id              INTEGER PRIMARY KEY (auto-increment)
├── timestamp       DATETIME (auto-generated)
├── thermocouple_id INTEGER (1-8)
└── temperature     REAL (calibrated value in °C)
```

### What Gets Stored
- ✅ Every temperature reading from all channels
- ✅ Exact timestamp of each reading
- ✅ Calibrated temperature (after correction factor applied)
- ✅ Channel/thermocouple ID

### Example Data
```
id | timestamp           | thermocouple_id | temperature
---+---------------------+-----------------+------------
1  | 2025-10-01 14:23:45 | 1              | 25.3
2  | 2025-10-01 14:23:45 | 2              | 26.1
3  | 2025-10-01 14:23:50 | 1              | 25.4
```

### Used By
- **Web Dashboard** - Real-time charts and graphs
- **API Endpoints** - `/api/data/latest`, `/api/data/historical`
- **Data Export** - Download as CSV/JSON from web interface
- **Analytics** - Average temperatures, min/max calculations

### Size
- Current: ~28 KB
- Grows approximately: **1-2 MB per day** (with 8 channels at 5-second intervals)
- After 1 month: ~30-60 MB
- After 1 year: ~365-730 MB

---

## 2️⃣ Text File Storage (Backup)

### Location
```
data-logger-project/data/
├── raw/              ← Hourly files (current hour)
├── daily/            ← Consolidated daily files
└── compressed/       ← Compressed archive (.gz)
```

### File Naming Convention
```
raw/2025-10-01_14.txt          ← Hour 14 (2 PM) on Oct 1
daily/2025-10-01.txt           ← Full day Oct 1
compressed/2025-09-01.txt.gz   ← Compressed Sept 1
```

### File Format (CSV)
```
timestamp,channel,raw_temp,calibrated_temp
2025-10-01 14:23:45,1,25.3,25.3
2025-10-01 14:23:45,2,26.1,26.1
2025-10-01 14:23:50,1,25.4,25.4
```

### Automatic Management
1. **Hourly Files** - Created in `raw/` folder as data is logged
2. **Daily Consolidation** - At end of day, hourly files → one daily file
3. **Compression** - Old daily files (>7 days) are compressed to .gz
4. **Cleanup** - Very old compressed files (>90 days) can be auto-deleted

### Used For
- 📦 **Long-term backup** - Won't lose data if database fails
- 🚀 **Fast export** - Direct CSV download without database query
- 💾 **Low resource** - Text files are smaller and faster to write
- 🔄 **Data recovery** - Can rebuild database from text files

### Size
- Text files are **smaller** than database
- Compressed files are **80-90% smaller**
- Example: 100 MB of data → 10-20 MB compressed

---

## 📊 Data Flow Diagram

```
Temperature Reading
        ↓
    [Calibration]
        ↓
   ┌────┴────┐
   ↓         ↓
[SQLite]  [Text File]
   ↓         ↓
[Dashboard] [Backup]
```

### When You Log Data:

1. **Sensor reads temperature** (e.g., 25.3°C)
2. **Calibration applied** (multiply by correction factor)
3. **Stored in TWO places simultaneously:**
   - SQLite database (`datalogger.db`)
   - Text file (`data/raw/2025-10-01_14.txt`)

---

## 🔍 How to View Your Data

### Option 1: Web Dashboard
```
http://localhost:8080
```
- View real-time charts
- See historical graphs
- Download CSV/JSON exports

### Option 2: SQLite Browser (Direct Database Access)
```bash
# Install SQLite browser
sudo apt install sqlitebrowser

# Open database
sqlitebrowser data-logger-project/datalogger.db
```

### Option 3: Text Files (Direct Access)
```bash
# View today's raw data
cat data-logger-project/data/raw/2025-10-01_14.txt

# View daily consolidated
cat data-logger-project/data/daily/2025-10-01.txt

# View compressed (auto-decompresses)
zcat data-logger-project/data/compressed/2025-09-01.txt.gz
```

### Option 4: Python Script
```python
import sqlite3

conn = sqlite3.connect('datalogger.db')
cursor = conn.cursor()

# Get latest readings
cursor.execute("SELECT * FROM readings ORDER BY timestamp DESC LIMIT 10")
for row in cursor.fetchall():
    print(row)

conn.close()
```

---

## 💾 Storage Management

### Current Storage Usage
```bash
# Check database size
du -h data-logger-project/datalogger.db

# Check text files size
du -h data-logger-project/data/
```

### Clear Old Data

#### Option 1: From Web Interface
```
http://localhost:8080
→ Click "Clear Historical Data" button
```

#### Option 2: Manual Database Clear
```bash
cd data-logger-project
python3 << EOF
from database import clear_all_data
clear_all_data()
print("Database cleared!")
EOF
```

#### Option 3: Delete Old Text Files
```bash
# Delete files older than 30 days
find data-logger-project/data/compressed/ -type f -mtime +30 -delete
```

---

## 🔄 Data Export Options

### 1. From Web Dashboard
- Go to http://localhost:8080
- Click "Export" section
- Choose: CSV or JSON
- Select date range
- Download

### 2. Direct Database Export
```bash
# Export to CSV
sqlite3 -header -csv datalogger.db "SELECT * FROM readings;" > export.csv

# Export to JSON
sqlite3 datalogger.db << EOF
.mode json
.output export.json
SELECT * FROM readings;
.quit
EOF
```

### 3. Copy Text Files
```bash
# Copy all raw data
cp -r data-logger-project/data/ /path/to/backup/
```

---

## 📈 Storage Estimates

### 8 Channels at 5-Second Intervals:

| Duration | Database Size | Text Files (Raw) | Text Files (Compressed) |
|----------|--------------|------------------|------------------------|
| 1 Hour   | ~100 KB      | ~50 KB          | ~10 KB                |
| 1 Day    | ~2 MB        | ~1 MB           | ~200 KB               |
| 1 Week   | ~14 MB       | ~7 MB           | ~1.4 MB               |
| 1 Month  | ~60 MB       | ~30 MB          | ~6 MB                 |
| 1 Year   | ~730 MB      | ~365 MB         | ~73 MB                |

### Storage Recommendations:
- **Raspberry Pi 5** with 32GB+ SD card: No problem, can store 1+ year
- **Enable compression**: Auto-compresses after 7 days
- **Auto-cleanup**: Delete compressed files after 90 days
- **Regular backups**: Copy to USB/cloud monthly

---

## 🛡️ Data Safety Features

### Automatic Protection:
✅ **Dual storage** - Data in both database and text files
✅ **Hourly backups** - New text file every hour
✅ **Daily consolidation** - Organized daily archives
✅ **Compression** - Old data compressed automatically
✅ **Gitignored** - Database won't be committed to GitHub (too large)

### If Database Corrupts:
1. Text files are still intact
2. Can rebuild database from text files
3. No data loss!

### If Text Files Deleted:
1. Database still has all data
2. Can export from web interface
3. Can recreate text files from database

---

## 🔧 Configuration Files

### Database Settings
File: `data-logger-project/config.json`
```json
{
  "database": {
    "type": "sqlite",
    "path": "datalogger.db",
    "backup_enabled": true
  }
}
```

### Text Logger Settings
File: `data-logger-project/config.json`
```json
{
  "logging": {
    "text_files_enabled": true,
    "compression_enabled": true,
    "cleanup_days": 90
  }
}
```

---

## 📊 Summary

### Your Data is Stored In:

1. **SQLite Database** (`datalogger.db`)
   - ✅ Fast queries
   - ✅ Real-time dashboard
   - ✅ Historical charts
   - Current size: ~28 KB

2. **Text Files** (`data/raw/`, `data/daily/`, `data/compressed/`)
   - ✅ Long-term backup
   - ✅ Easy to read/export
   - ✅ Compressed archives
   - Auto-managed

### Both Systems Run Simultaneously
- Every reading saved to **BOTH** locations
- Maximum data safety
- Flexible export options

---

**Your data is safe, organized, and easily accessible!** 📊✅
