import sqlite3
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from config import config

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    print("PostgreSQL support not available. Install psycopg2-binary for PostgreSQL support.")

class DatabaseInterface(ABC):
    @abstractmethod
    def connect(self):
        pass
    
    @abstractmethod
    def disconnect(self):
        pass
    
    @abstractmethod
    def create_tables(self):
        pass
    
    @abstractmethod
    def insert_reading(self, thermocouple_id: int, temperature: float):
        pass
    
    @abstractmethod
    def get_latest_readings(self) -> List[Dict]:
        pass
    
    @abstractmethod
    def get_historical_data(self, hours: int = 24) -> List[Dict]:
        pass
    
    @abstractmethod
    def get_data_by_range(self, start_date: datetime, end_date: datetime, channel: Optional[int] = None) -> List[Dict]:
        pass
    
    @abstractmethod
    def clear_all_data(self):
        pass
    
    @abstractmethod
    def get_storage_info(self) -> Dict:
        pass

class SQLiteDatabase(DatabaseInterface):
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.get('database.sqlite.path', 'datalogger.db')
        self.conn = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
    
    def disconnect(self):
        if self.conn:
            self.conn.close()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                thermocouple_id INTEGER,
                temperature REAL
            )
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp ON readings(timestamp)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_thermocouple ON readings(thermocouple_id)
        ''')
        self.conn.commit()
    
    def insert_reading(self, thermocouple_id: int, temperature: float):
        cursor = self.conn.cursor()
        # Use explicit local timestamp instead of CURRENT_TIMESTAMP (which is UTC)
        cursor.execute(
            'INSERT INTO readings (timestamp, thermocouple_id, temperature) VALUES (?, ?, ?)',
            (datetime.now().isoformat(), thermocouple_id, temperature)
        )
        self.conn.commit()
    
    def get_latest_readings(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT r1.* FROM readings r1
            INNER JOIN (
                SELECT thermocouple_id, MAX(timestamp) as max_time
                FROM readings
                GROUP BY thermocouple_id
            ) r2 ON r1.thermocouple_id = r2.thermocouple_id 
            AND r1.timestamp = r2.max_time
            ORDER BY r1.thermocouple_id
        ''')
        return [dict(row) for row in cursor.fetchall()]
    
    def get_historical_data(self, hours: int = 24) -> List[Dict]:
        cursor = self.conn.cursor()
        cutoff_time = datetime.now() - timedelta(hours=hours)
        cursor.execute('''
            SELECT * FROM readings
            WHERE timestamp > ?
            ORDER BY timestamp DESC
        ''', (cutoff_time.isoformat(),))  # Convert to ISO format string
        return [dict(row) for row in cursor.fetchall()]
    
    def get_data_by_range(self, start_date: datetime, end_date: datetime, channel: Optional[int] = None) -> List[Dict]:
        cursor = self.conn.cursor()
        if channel:
            cursor.execute('''
                SELECT * FROM readings
                WHERE timestamp BETWEEN ? AND ? AND thermocouple_id = ?
                ORDER BY timestamp
            ''', (start_date.isoformat(), end_date.isoformat(), channel))
        else:
            cursor.execute('''
                SELECT * FROM readings
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp
            ''', (start_date.isoformat(), end_date.isoformat()))
        return [dict(row) for row in cursor.fetchall()]
    
    def clear_all_data(self):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM readings')
        self.conn.commit()
    
    def get_storage_info(self) -> Dict:
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM readings')
        record_count = cursor.fetchone()['count']
        
        db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
        
        return {
            'type': 'SQLite',
            'path': self.db_path,
            'size_bytes': db_size,
            'size_mb': round(db_size / (1024 * 1024), 2),
            'record_count': record_count
        }

class PostgreSQLDatabase(DatabaseInterface):
    def __init__(self):
        if not POSTGRES_AVAILABLE:
            raise ImportError("PostgreSQL support not available. Install psycopg2-binary")
        
        self.conn_params = {
            'host': config.get('database.postgresql.host', 'localhost'),
            'port': config.get('database.postgresql.port', 5432),
            'database': config.get('database.postgresql.database', 'datalogger'),
            'user': config.get('database.postgresql.username', ''),
            'password': config.get('database.postgresql.password', ''),
            'sslmode': config.get('database.postgresql.ssl_mode', 'prefer')
        }
        self.conn = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        try:
            self.conn = psycopg2.connect(**self.conn_params)
            self.conn.autocommit = True
        except psycopg2.Error as e:
            print(f"PostgreSQL connection error: {e}")
            raise
    
    def disconnect(self):
        if self.conn:
            self.conn.close()
    
    def create_tables(self):
        with self.conn.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS readings (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    thermocouple_id INTEGER,
                    temperature REAL
                )
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp ON readings(timestamp)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_thermocouple ON readings(thermocouple_id)
            ''')
    
    def insert_reading(self, thermocouple_id: int, temperature: float):
        with self.conn.cursor() as cursor:
            cursor.execute(
                'INSERT INTO readings (thermocouple_id, temperature) VALUES (%s, %s)',
                (thermocouple_id, temperature)
            )
    
    def get_latest_readings(self) -> List[Dict]:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('''
                SELECT DISTINCT ON (thermocouple_id) 
                    id, timestamp, thermocouple_id, temperature
                FROM readings
                ORDER BY thermocouple_id, timestamp DESC
            ''')
            return cursor.fetchall()
    
    def get_historical_data(self, hours: int = 24) -> List[Dict]:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('''
                SELECT * FROM readings 
                WHERE timestamp > NOW() - INTERVAL '%s hours'
                ORDER BY timestamp DESC
            ''', (hours,))
            return cursor.fetchall()
    
    def get_data_by_range(self, start_date: datetime, end_date: datetime, channel: Optional[int] = None) -> List[Dict]:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            if channel:
                cursor.execute('''
                    SELECT * FROM readings 
                    WHERE timestamp BETWEEN %s AND %s AND thermocouple_id = %s
                    ORDER BY timestamp
                ''', (start_date, end_date, channel))
            else:
                cursor.execute('''
                    SELECT * FROM readings 
                    WHERE timestamp BETWEEN %s AND %s
                    ORDER BY timestamp
                ''', (start_date, end_date))
            return cursor.fetchall()
    
    def clear_all_data(self):
        with self.conn.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE readings')
    
    def get_storage_info(self) -> Dict:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute('SELECT COUNT(*) as count FROM readings')
            record_count = cursor.fetchone()['count']
            
            cursor.execute('''
                SELECT pg_database_size(current_database()) as size
            ''')
            db_size = cursor.fetchone()['size']
        
        return {
            'type': 'PostgreSQL',
            'host': self.conn_params['host'],
            'database': self.conn_params['database'],
            'size_bytes': db_size,
            'size_mb': round(db_size / (1024 * 1024), 2),
            'record_count': record_count
        }

class DualDatabaseManager:
    """Manages dual database storage - writes to both SQLite and PostgreSQL simultaneously"""

    def __init__(self, sqlite_db: SQLiteDatabase, postgres_db: PostgreSQLDatabase):
        self.sqlite_db = sqlite_db
        self.postgres_db = postgres_db
        self.active = True

    def insert_reading(self, thermocouple_id: int, temperature: float):
        """Insert reading to both databases"""
        errors = []

        # Try SQLite
        try:
            self.sqlite_db.insert_reading(thermocouple_id, temperature)
        except Exception as e:
            errors.append(f"SQLite: {e}")

        # Try PostgreSQL
        try:
            self.postgres_db.insert_reading(thermocouple_id, temperature)
        except Exception as e:
            errors.append(f"PostgreSQL: {e}")

        if errors:
            print(f"[DualDB] Errors during insert: {', '.join(errors)}")

    def get_latest_readings(self) -> List[Dict]:
        """Get latest readings (from SQLite as primary)"""
        try:
            return self.sqlite_db.get_latest_readings()
        except Exception as e:
            print(f"[DualDB] SQLite failed, trying PostgreSQL: {e}")
            return self.postgres_db.get_latest_readings()

    def get_historical_data(self, hours: int = 24) -> List[Dict]:
        """Get historical data (from SQLite as primary)"""
        try:
            return self.sqlite_db.get_historical_data(hours)
        except Exception as e:
            print(f"[DualDB] SQLite failed, trying PostgreSQL: {e}")
            return self.postgres_db.get_historical_data(hours)

    def get_data_by_range(self, start_date: datetime, end_date: datetime, channel: Optional[int] = None) -> List[Dict]:
        """Get data by range (from SQLite as primary)"""
        try:
            return self.sqlite_db.get_data_by_range(start_date, end_date, channel)
        except Exception as e:
            print(f"[DualDB] SQLite failed, trying PostgreSQL: {e}")
            return self.postgres_db.get_data_by_range(start_date, end_date, channel)

    def clear_all_data(self):
        """Clear data from both databases"""
        errors = []

        try:
            self.sqlite_db.clear_all_data()
        except Exception as e:
            errors.append(f"SQLite: {e}")

        try:
            self.postgres_db.clear_all_data()
        except Exception as e:
            errors.append(f"PostgreSQL: {e}")

        if errors:
            print(f"[DualDB] Errors during clear: {', '.join(errors)}")

    def get_storage_info(self) -> Dict:
        """Get storage info from both databases"""
        sqlite_info = {}
        postgres_info = {}

        try:
            sqlite_info = self.sqlite_db.get_storage_info()
        except Exception as e:
            sqlite_info = {'error': str(e)}

        try:
            postgres_info = self.postgres_db.get_storage_info()
        except Exception as e:
            postgres_info = {'error': str(e)}

        return {
            'type': 'Dual (SQLite + PostgreSQL)',
            'sqlite': sqlite_info,
            'postgresql': postgres_info
        }

    def disconnect(self):
        """Disconnect both databases"""
        try:
            self.sqlite_db.disconnect()
        except Exception as e:
            print(f"[DualDB] Error disconnecting SQLite: {e}")

        try:
            self.postgres_db.disconnect()
        except Exception as e:
            print(f"[DualDB] Error disconnecting PostgreSQL: {e}")

class DatabaseManager:
    def __init__(self):
        self.db = None
        self.db_type = config.get('database.type', 'sqlite')
        self.sqlite_instance = None
        self.postgres_instance = None
        self.initialize_database()

    def initialize_database(self):
        if self.db_type == 'postgresql' and POSTGRES_AVAILABLE:
            try:
                self.db = PostgreSQLDatabase()
                self.postgres_instance = self.db
                print("Connected to PostgreSQL database")
            except Exception as e:
                print(f"Failed to connect to PostgreSQL: {e}, falling back to SQLite")
                self.db_type = 'sqlite'
                self.db = SQLiteDatabase()
                self.sqlite_instance = self.db
        elif self.db_type == 'both':
            # Dual database mode
            try:
                self.sqlite_instance = SQLiteDatabase()
                print("SQLite database initialized")
            except Exception as e:
                print(f"Failed to initialize SQLite: {e}")
                self.sqlite_instance = None

            try:
                if POSTGRES_AVAILABLE:
                    self.postgres_instance = PostgreSQLDatabase()
                    print("PostgreSQL database initialized")
                else:
                    print("PostgreSQL not available, skipping")
                    self.postgres_instance = None
            except Exception as e:
                print(f"Failed to initialize PostgreSQL: {e}")
                self.postgres_instance = None

            if self.sqlite_instance and self.postgres_instance:
                self.db = DualDatabaseManager(self.sqlite_instance, self.postgres_instance)
                print("Using DUAL database mode (SQLite + PostgreSQL)")
            elif self.sqlite_instance:
                self.db = self.sqlite_instance
                self.db_type = 'sqlite'
                print("PostgreSQL unavailable, using SQLite only")
            else:
                raise Exception("Failed to initialize any database")
        else:
            self.db = SQLiteDatabase()
            self.sqlite_instance = self.db
            print("Using SQLite database")

    def switch_database(self, db_type: str, **kwargs):
        """Switch database mode: 'sqlite', 'postgresql', or 'both'"""
        if self.db:
            self.db.disconnect()

        if db_type == 'postgresql':
            if not POSTGRES_AVAILABLE:
                raise ImportError("PostgreSQL support not available")

            # Update config if kwargs provided
            if kwargs:
                for key, value in kwargs.items():
                    config.set(f'database.postgresql.{key}', value)

            self.postgres_instance = PostgreSQLDatabase()
            self.db = self.postgres_instance
            config.set('database.type', 'postgresql')

        elif db_type == 'both':
            # Initialize both databases
            if 'sqlite_path' in kwargs:
                config.set('database.sqlite.path', kwargs['sqlite_path'])

            if kwargs:
                for key, value in kwargs.items():
                    if key.startswith('pg_'):
                        config.set(f'database.postgresql.{key[3:]}', value)

            self.sqlite_instance = SQLiteDatabase()

            if POSTGRES_AVAILABLE:
                self.postgres_instance = PostgreSQLDatabase()
                self.db = DualDatabaseManager(self.sqlite_instance, self.postgres_instance)
                config.set('database.type', 'both')
            else:
                print("PostgreSQL not available, using SQLite only")
                self.db = self.sqlite_instance
                config.set('database.type', 'sqlite')

        else:  # sqlite
            if 'path' in kwargs:
                config.set('database.sqlite.path', kwargs['path'])
            self.sqlite_instance = SQLiteDatabase()
            self.db = self.sqlite_instance
            config.set('database.type', 'sqlite')

        self.db_type = db_type

    def get_connection_status(self) -> Dict:
        status = {
            'connected': self.db is not None,
            'type': self.db_type,
            'info': self.db.get_storage_info() if self.db else {}
        }

        # Add individual database status for dual mode
        if self.db_type == 'both':
            status['sqlite_connected'] = self.sqlite_instance is not None
            status['postgres_connected'] = self.postgres_instance is not None

        return status

    def __getattr__(self, name):
        # Proxy all other calls to the database instance
        if self.db and hasattr(self.db, name):
            return getattr(self.db, name)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")