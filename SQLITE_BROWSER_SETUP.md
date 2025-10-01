# 🗄️ SQLite Browser Setup for Raspberry Pi 5

Using **SQLite Browser** gives you a professional database GUI to view and analyze your data!

---

## ✨ Why Use SQLite Browser?

### Advantages:
- ✅ **Visual table view** - See all data in spreadsheet format
- ✅ **Sort & filter** - Click column headers to sort
- ✅ **Search** - Find specific readings instantly
- ✅ **Custom queries** - Run SQL commands
- ✅ **Export options** - Export to CSV, SQL, JSON
- ✅ **Database structure** - See table schema
- ✅ **Professional tool** - Used by developers worldwide

### Perfect For:
- 📊 Detailed data analysis
- 🔍 Finding specific temperature readings
- 📈 Calculating averages, min/max
- 🛠️ Advanced SQL queries
- 📋 Quick copy/paste of data

---

## 📦 Installation (One-Time Setup)

### On Raspberry Pi 5:

```bash
# Update package list
sudo apt update

# Install SQLite Browser
sudo apt install sqlitebrowser

# That's it! ✅
```

**Installation size:** ~15 MB
**Installation time:** ~1 minute

---

## 🚀 How to Use

### Method 1: From Desktop (Double-click)

1. **Open File Manager**
2. Navigate to: `/home/pi/DataLogger/data-logger-project/`
3. **Right-click** on `datalogger.db`
4. Select **"Open With SQLite Browser"**

### Method 2: From Terminal

```bash
# Navigate to project
cd ~/DataLogger/data-logger-project

# Open database
sqlitebrowser datalogger.db

# Or just:
sqlitebrowser datalogger.db &
```

### Method 3: From Applications Menu

1. Click **Applications Menu**
2. Find **"SQLite Browser"** or **"DB Browser for SQLite"**
3. Click **File → Open Database**
4. Navigate to: `/home/pi/DataLogger/data-logger-project/datalogger.db`

---

## 📊 SQLite Browser Interface

When you open the database, you'll see:

### 1️⃣ **Database Structure Tab**
- See the `readings` table
- View column definitions:
  - `id` - Unique record ID
  - `timestamp` - When reading was taken
  - `thermocouple_id` - Channel number (1-8)
  - `temperature` - Calibrated temperature value

### 2️⃣ **Browse Data Tab** ⭐ Most Useful
```
┌─────────────────────────────────────────────────────┐
│ id │ timestamp           │ thermocouple_id │ temp   │
├────┼────────────────────┼─────────────────┼────────┤
│ 1  │ 2025-10-01 14:23:45│ 1               │ 25.3   │
│ 2  │ 2025-10-01 14:23:45│ 2               │ 26.1   │
│ 3  │ 2025-10-01 14:23:50│ 1               │ 25.4   │
└────┴────────────────────┴─────────────────┴────────┘
```

**Features:**
- Click column headers to **sort**
- Type in filter box to **search**
- **Scroll** through all records
- **Copy** selected rows
- See record count at bottom

### 3️⃣ **Execute SQL Tab** (Advanced)
Run custom queries:

```sql
-- Get latest readings for each channel
SELECT thermocouple_id, temperature, timestamp
FROM readings
WHERE id IN (
    SELECT MAX(id)
    FROM readings
    GROUP BY thermocouple_id
)
ORDER BY thermocouple_id;

-- Get average temperature per channel
SELECT
    thermocouple_id as Channel,
    COUNT(*) as Readings,
    ROUND(AVG(temperature), 2) as Average,
    ROUND(MIN(temperature), 2) as Minimum,
    ROUND(MAX(temperature), 2) as Maximum
FROM readings
GROUP BY thermocouple_id
ORDER BY thermocouple_id;

-- Get readings from last hour
SELECT *
FROM readings
WHERE timestamp >= datetime('now', '-1 hour')
ORDER BY timestamp DESC;

-- Get readings for specific channel
SELECT timestamp, temperature
FROM readings
WHERE thermocouple_id = 1
ORDER BY timestamp DESC
LIMIT 100;
```

---

## 🎯 Common Tasks

### Task 1: View All Recent Data
1. Open SQLite Browser
2. Go to **"Browse Data"** tab
3. Select table: `readings`
4. Click **timestamp** column header to sort
5. Scroll to see latest readings

### Task 2: Find Highest Temperature
1. Go to **"Execute SQL"** tab
2. Run this query:
```sql
SELECT timestamp, thermocouple_id, temperature
FROM readings
ORDER BY temperature DESC
LIMIT 10;
```
3. See top 10 highest readings

### Task 3: Export to CSV
1. Go to **"Browse Data"** tab
2. Click **File → Export → Table as CSV**
3. Choose filename
4. Click Save

### Task 4: See Channel Statistics
1. Go to **"Execute SQL"** tab
2. Run:
```sql
SELECT
    thermocouple_id,
    COUNT(*) as total_readings,
    ROUND(AVG(temperature), 2) as avg_temp,
    ROUND(MIN(temperature), 2) as min_temp,
    ROUND(MAX(temperature), 2) as max_temp
FROM readings
GROUP BY thermocouple_id;
```

### Task 5: Filter by Date Range
1. Go to **"Execute SQL"** tab
2. Run:
```sql
SELECT *
FROM readings
WHERE timestamp BETWEEN '2025-10-01 00:00:00' AND '2025-10-01 23:59:59'
ORDER BY timestamp;
```

---

## 💡 Pro Tips

### Tip 1: Read-Only Mode
If you just want to view (not edit):
```bash
sqlitebrowser -R datalogger.db
```
This prevents accidental changes.

### Tip 2: Quick Filters
In Browse Data tab:
- Type in **Filter** box to search
- Use wildcards: `CH 1` finds all Channel 1 readings
- Clear filter to see all data again

### Tip 3: Save Favorite Queries
1. Write a useful SQL query
2. Click **File → Save SQL**
3. Reuse later from **File → Open SQL**

### Tip 4: Copy Data
1. Select rows in Browse Data tab
2. Right-click → **Copy**
3. Paste into Excel, LibreOffice, etc.

### Tip 5: Refresh Data
If DataLogger is running and adding new data:
- Press **F5** or click **Refresh** button
- See latest readings instantly

---

## 🔐 Safety Features

### SQLite Browser is Safe:
- ✅ **Read-only option** - Can't accidentally delete data
- ✅ **Transaction support** - Can undo changes
- ✅ **Backup reminder** - Warns before making changes
- ✅ **Non-destructive** - Original file stays safe

### Best Practices:
1. **Always open in read-only mode** if just viewing:
   ```bash
   sqlitebrowser -R datalogger.db
   ```

2. **Close SQLite Browser** before clearing database from web interface

3. **Don't edit structure** - Let the application manage it

---

## 📊 Screenshot of What You'll See

```
┌─────────────────────────────────────────────────────────────┐
│ DB Browser for SQLite - datalogger.db                       │
├─────────────────────────────────────────────────────────────┤
│ [Database Structure] [Browse Data] [Execute SQL] [DB Schema]│
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ Table: readings                           Records: 1,245    │
│ ┌────────────────────────────────────────────────────────┐ │
│ │ Filter: _____________________________________ [Clear]  │ │
│ └────────────────────────────────────────────────────────┘ │
│                                                              │
│ ┌─────┬──────────────────────┬──────────────┬─────────────┐│
│ │ id  │ timestamp            │ thermocouple │ temperature ││
│ ├─────┼──────────────────────┼──────────────┼─────────────┤│
│ │ 1   │ 2025-10-01 14:23:45 │ 1            │ 25.3        ││
│ │ 2   │ 2025-10-01 14:23:45 │ 2            │ 26.1        ││
│ │ 3   │ 2025-10-01 14:23:50 │ 1            │ 25.4        ││
│ │ ... │ ...                  │ ...          │ ...         ││
│ └─────┴──────────────────────┴──────────────┴─────────────┘│
│                                                              │
│ [First] [Previous] [Next] [Last]         Row: 1 of 1,245   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🆚 Comparison: Web Dashboard vs SQLite Browser

| Feature | Web Dashboard | SQLite Browser |
|---------|---------------|----------------|
| **Charts/Graphs** | ✅ Yes | ❌ No |
| **Table View** | ⚠️ Limited | ✅ Full table |
| **Sort/Filter** | ⚠️ Basic | ✅ Advanced |
| **SQL Queries** | ❌ No | ✅ Yes |
| **Export CSV** | ✅ Yes | ✅ Yes |
| **Real-time** | ✅ Yes | ⚠️ Manual refresh |
| **Installation** | ❌ No install | ✅ Needs install |

**Best approach:** Use **both**!
- 📊 **Web Dashboard** for charts and monitoring
- 🗄️ **SQLite Browser** for detailed analysis

---

## 🔧 Troubleshooting

### Issue: "Database is locked"
**Cause:** DataLogger app is writing to database

**Solution:**
1. Stop DataLogger temporarily
2. Open SQLite Browser in read-only mode:
   ```bash
   sqlitebrowser -R datalogger.db
   ```

### Issue: "No such table: readings"
**Cause:** Database not initialized yet

**Solution:**
1. Start DataLogger app once
2. It will create the table automatically

### Issue: Can't find sqlitebrowser command
**Solution:**
```bash
# Reinstall
sudo apt install sqlitebrowser

# Or find it in applications menu
# Search for "DB Browser for SQLite"
```

---

## 📚 Useful SQL Queries

Copy and paste these into **Execute SQL** tab:

### Get Latest 100 Readings
```sql
SELECT * FROM readings
ORDER BY timestamp DESC
LIMIT 100;
```

### Today's Data Only
```sql
SELECT * FROM readings
WHERE DATE(timestamp) = DATE('now')
ORDER BY timestamp;
```

### Hourly Averages
```sql
SELECT
    strftime('%Y-%m-%d %H:00', timestamp) as hour,
    thermocouple_id,
    ROUND(AVG(temperature), 2) as avg_temp
FROM readings
GROUP BY hour, thermocouple_id
ORDER BY hour DESC;
```

### Count Records Per Channel
```sql
SELECT
    thermocouple_id,
    COUNT(*) as count
FROM readings
GROUP BY thermocouple_id
ORDER BY thermocouple_id;
```

### Find Temperature Spikes
```sql
SELECT * FROM readings
WHERE temperature > 30.0
ORDER BY temperature DESC;
```

---

## ✅ Summary

**Yes, SQLite Browser is excellent!**

### Quick Setup:
```bash
sudo apt install sqlitebrowser
sqlitebrowser ~/DataLogger/data-logger-project/datalogger.db
```

### Best For:
- ✅ Detailed data inspection
- ✅ Custom SQL queries
- ✅ Sorting and filtering
- ✅ Professional analysis

### Use Together With:
- 📊 Web dashboard (for charts)
- 🐍 Python viewer (for quick stats)
- 📄 Text files (for backup)

---

**Recommendation:** Install it! It's a powerful tool that complements the web dashboard perfectly. 🚀
