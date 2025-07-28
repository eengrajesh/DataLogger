import sqlite3
from datetime import datetime, timedelta

DATABASE_NAME = 'datalogger.db'

def get_db_connection():
    """Establishes a connection to the database."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database and creates the 'readings' table if it doesn't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            thermocouple_id INTEGER NOT NULL,
            temperature REAL NOT NULL
        );
    ''')
    conn.commit()
    conn.close()

def add_reading(thermocouple_id, temperature):
    """Adds a new temperature reading to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO readings (thermocouple_id, temperature) VALUES (?, ?)",
        (thermocouple_id, temperature)
    )
    conn.commit()
    conn.close()

def get_latest_readings():
    """Fetches the most recent reading for each thermocouple."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT r1.*
        FROM readings r1
        JOIN (
            SELECT thermocouple_id, MAX(timestamp) AS max_ts
            FROM readings
            GROUP BY thermocouple_id
        ) r2 ON r1.thermocouple_id = r2.thermocouple_id AND r1.timestamp = r2.max_ts
        ORDER BY r1.thermocouple_id;
    ''')
    readings = cursor.fetchall()
    conn.close()
    return [dict(row) for row in readings]

def get_historical_data(hours=1):
    """Fetches historical data for all thermocouples within a given time window."""
    conn = get_db_connection()
    cursor = conn.cursor()
    time_threshold = datetime.now() - timedelta(hours=hours)
    
    cursor.execute(
        "SELECT * FROM readings WHERE timestamp >= ? ORDER BY timestamp",
        (time_threshold,)
    )
    readings = cursor.fetchall()
    conn.close()
    return [dict(row) for row in readings]

if __name__ == '__main__':
    # This allows us to initialize the database from the command line
    print("Initializing database...")
    init_db()
    print("Database initialized.")