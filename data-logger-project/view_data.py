#!/usr/bin/env python3
"""
Simple Data Viewer - No Installation Required!
Just run: python3 view_data.py
"""

import sqlite3
import os
from datetime import datetime

DB_FILE = 'datalogger.db'

def view_database():
    """View data from SQLite database"""

    if not os.path.exists(DB_FILE):
        print("❌ Database not found!")
        print("   Start the DataLogger application first to create data.")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    print("=" * 80)
    print("  📊 DATALOGGER - DATA VIEWER")
    print("=" * 80)

    # Total records
    cursor.execute("SELECT COUNT(*) FROM readings")
    total = cursor.fetchone()[0]
    print(f"\n📈 Total Records: {total:,}")

    if total == 0:
        print("\n⚠️  No data yet. Start logging to see data here!")
        conn.close()
        return

    # Date range
    cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM readings")
    min_date, max_date = cursor.fetchone()
    print(f"📅 Date Range: {min_date} to {max_date}")

    # Per-channel statistics
    cursor.execute("""
        SELECT
            thermocouple_id as channel,
            COUNT(*) as records,
            ROUND(AVG(temperature), 2) as avg_temp,
            ROUND(MIN(temperature), 2) as min_temp,
            ROUND(MAX(temperature), 2) as max_temp
        FROM readings
        GROUP BY thermocouple_id
        ORDER BY thermocouple_id
    """)

    stats = cursor.fetchall()

    print("\n" + "=" * 80)
    print("  📊 STATISTICS BY CHANNEL")
    print("=" * 80)
    print(f"{'Channel':<10} {'Records':<12} {'Average':<12} {'Min':<12} {'Max':<12}")
    print("-" * 80)

    for row in stats:
        channel, records, avg, min_t, max_t = row
        print(f"CH {channel:<7} {records:<12,} {avg:<12}°C {min_t:<12}°C {max_t:<12}°C")

    # Recent readings
    print("\n" + "=" * 80)
    print("  🕒 LATEST 20 READINGS")
    print("=" * 80)
    print(f"{'Timestamp':<20} {'Channel':<10} {'Temperature':<15}")
    print("-" * 80)

    cursor.execute("""
        SELECT timestamp, thermocouple_id, ROUND(temperature, 2)
        FROM readings
        ORDER BY timestamp DESC
        LIMIT 20
    """)

    for row in cursor.fetchall():
        timestamp, channel, temp = row
        print(f"{timestamp:<20} CH {channel:<8} {temp:<15}°C")

    # Database size
    db_size = os.path.getsize(DB_FILE)
    print("\n" + "=" * 80)
    print(f"💾 Database Size: {db_size:,} bytes ({db_size/1024:.2f} KB)")
    print("=" * 80)

    conn.close()

def export_to_csv():
    """Export all data to CSV file"""

    if not os.path.exists(DB_FILE):
        print("❌ Database not found!")
        return

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    filename = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    print(f"\n📤 Exporting to: {filename}")

    cursor.execute("SELECT * FROM readings ORDER BY timestamp")

    with open(filename, 'w') as f:
        # Write header
        f.write("id,timestamp,channel,temperature\n")

        # Write data
        for row in cursor.fetchall():
            f.write(f"{row[0]},{row[1]},{row[2]},{row[3]}\n")

    print(f"✅ Export complete: {filename}")

    conn.close()

def view_text_files():
    """View data from text files"""

    data_dir = 'data'

    if not os.path.exists(data_dir):
        print("❌ No text files found yet!")
        return

    print("\n" + "=" * 80)
    print("  📁 TEXT FILES")
    print("=" * 80)

    # List raw files
    raw_dir = os.path.join(data_dir, 'raw')
    if os.path.exists(raw_dir):
        raw_files = os.listdir(raw_dir)
        if raw_files:
            print(f"\n📄 Raw Files ({len(raw_files)} files):")
            for f in sorted(raw_files)[-5:]:  # Show last 5
                filepath = os.path.join(raw_dir, f)
                size = os.path.getsize(filepath)
                print(f"  - {f} ({size:,} bytes)")

    # List daily files
    daily_dir = os.path.join(data_dir, 'daily')
    if os.path.exists(daily_dir):
        daily_files = os.listdir(daily_dir)
        if daily_files:
            print(f"\n📅 Daily Files ({len(daily_files)} files):")
            for f in sorted(daily_files)[-5:]:  # Show last 5
                filepath = os.path.join(daily_dir, f)
                size = os.path.getsize(filepath)
                print(f"  - {f} ({size:,} bytes)")

    # List compressed files
    comp_dir = os.path.join(data_dir, 'compressed')
    if os.path.exists(comp_dir):
        comp_files = os.listdir(comp_dir)
        if comp_files:
            print(f"\n🗜️  Compressed Files ({len(comp_files)} files):")
            for f in sorted(comp_files)[-5:]:  # Show last 5
                filepath = os.path.join(comp_dir, f)
                size = os.path.getsize(filepath)
                print(f"  - {f} ({size:,} bytes)")

def main():
    """Main menu"""

    while True:
        print("\n" + "=" * 80)
        print("  🌡️  DATALOGGER - DATA VIEWER MENU")
        print("=" * 80)
        print("\n1. View Database Statistics")
        print("2. Export Database to CSV")
        print("3. View Text Files Info")
        print("4. Exit")

        choice = input("\nSelect option (1-4): ").strip()

        if choice == '1':
            view_database()
        elif choice == '2':
            export_to_csv()
        elif choice == '3':
            view_text_files()
        elif choice == '4':
            print("\n👋 Goodbye!")
            break
        else:
            print("\n❌ Invalid choice. Try again.")

if __name__ == '__main__':
    main()
