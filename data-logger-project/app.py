#!/usr/bin/env python3
"""
Enertherm Temperature Data Logger System
Version 2.0.0 - October 2025

Professional multi-channel temperature monitoring with K-type thermocouples.
Supports real-time data logging, web dashboard, Telegram notifications,
and dual database storage (SQLite + PostgreSQL).

Copyright (c) 2025 Enertherm Engineering. All Rights Reserved.
Licensed for commercial use only.

Platform: Raspberry Pi 5 / Windows (development)
Hardware: Sequent Microsystems 8-Thermocouple DAQ HAT
"""

__version__ = "2.0.0"
__author__ = "Enertherm Engineering"
__copyright__ = "Copyright 2025, Enertherm Engineering"
__license__ = "Proprietary"

from flask import Flask, render_template, jsonify, request, send_file, send_from_directory
from database_manager import DatabaseManager
from storage_manager import StorageManager
from text_file_logger import text_file_logger
from notification_system import notification_system, AlertLevel
import sys
import os
import json
import time
import platform
from datetime import datetime, timedelta
from config import config

# Import data logger functions
try:
    from data_logger import (
        start_logging_thread, stop_logging_thread, daq,
        get_board_info, connect, disconnect,
        set_sensor_status, get_sensor_status,
        set_sensor_interval, get_sensor_intervals,
        get_cpu_temperature, is_logging, is_connected,
        set_database_manager
    )
    DATA_LOGGER_AVAILABLE = True
except ImportError as e:
    print(f"Data logger import warning: {e}")
    DATA_LOGGER_AVAILABLE = False

# Import Telegram bot
try:
    import requests
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("Requests library not available - Telegram disabled")

# Import the full Telegram bot
try:
    from telegram_bot import TelegramBot
    TELEGRAM_BOT_AVAILABLE = True
except ImportError:
    TELEGRAM_BOT_AVAILABLE = False
    print("Telegram bot module not available")

app = Flask(__name__)
db_manager = DatabaseManager()
storage_manager = StorageManager()

# Share database manager with data_logger module
if DATA_LOGGER_AVAILABLE:
    set_database_manager(db_manager)

# Application state
import time as time_module
app_state = {
    'logging_active': False,
    'daq_connected': False,
    'telegram_token': config.get('telegram.bot_token', ''),
    'admin_users': config.get('telegram.admin_users', []),
    'startup_time': datetime.now(),
    'start_time': time_module.time()
}

def send_telegram_message(message, chat_id=None):
    """Send Telegram message using simple HTTP requests"""
    if not TELEGRAM_AVAILABLE or not app_state['telegram_token']:
        return False

    try:
        url = f"https://api.telegram.org/bot{app_state['telegram_token']}/sendMessage"

        # Send to specific user or all admin users
        recipients = [chat_id] if chat_id else app_state['admin_users']

        for user_id in recipients:
            data = {
                'chat_id': user_id,
                'text': message,
                'parse_mode': 'Markdown'
            }

            response = requests.post(url, data=data, timeout=10)
            if response.status_code != 200:
                print(f"Telegram API error: {response.status_code}")

        return True
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")
        return False

# Create static directory
static_dir = os.path.join(os.path.dirname(__file__), 'static')
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/classic')
def classic():
    return render_template('index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    static_path = os.path.join(os.path.dirname(__file__), 'static')
    return send_from_directory(static_path, filename)

# ============= Connection Management =============
@app.route('/api/connect', methods=['POST'])
def api_connect():
    try:
        if DATA_LOGGER_AVAILABLE:
            result = connect()
            app_state['daq_connected'] = result
            if result:
                send_telegram_message("DAQ Connected - Hardware connection established")
                info = get_board_info()  # Returns {"board_info": {...}}
                return jsonify({
                    "status": "success",
                    "board_info": info["board_info"]  # Unwrap the nested board_info
                })
            else:
                return jsonify({"status": "failed", "message": "Connection failed"})
        else:
            app_state['daq_connected'] = True
            return jsonify({
                "status": "success",
                "board_info": {
                    "connected": True,
                    "simulated": True,
                    "type": "Mock DAQ",
                    "channels": 8
                }
            })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/disconnect', methods=['POST'])
def api_disconnect():
    try:
        if DATA_LOGGER_AVAILABLE:
            result = disconnect()
            app_state['daq_connected'] = False
            if result:
                return jsonify({
                    "status": "success",
                    "board_info": {
                        "connected": False
                    }
                })
            else:
                return jsonify({"status": "failed", "message": "Disconnect failed"})
        else:
            app_state['daq_connected'] = False
            return jsonify({
                "status": "success",
                "board_info": {
                    "connected": False,
                    "simulated": True
                }
            })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ============= Logging Control =============
@app.route('/api/logging/start', methods=['POST'])
def api_start_logging():
    try:
        if DATA_LOGGER_AVAILABLE:
            result = start_logging_thread()
            app_state['logging_active'] = result
            if result:
                send_telegram_message("**Logging Started** - Temperature data collection is now active")
        else:
            app_state['logging_active'] = True
            result = True
            send_telegram_message("**Logging Started** (Simulated mode)")

        return jsonify({
            "status": "success" if result else "failed",
            "message": "Logging started successfully" if result else "Failed to start logging",
            "logging_active": result
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/logging/stop', methods=['POST'])
def api_stop_logging():
    try:
        if DATA_LOGGER_AVAILABLE:
            result = stop_logging_thread()
            app_state['logging_active'] = False
            if result:
                send_telegram_message("**Logging Stopped** - Temperature data collection stopped")
        else:
            app_state['logging_active'] = False
            result = True
            send_telegram_message("**Logging Stopped** (Simulated mode)")

        return jsonify({
            "status": "success" if result else "failed",
            "message": "Logging stopped successfully" if result else "Failed to stop logging",
            "logging_active": False
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/logging/status')
def api_logging_status():
    try:
        if DATA_LOGGER_AVAILABLE:
            is_active = is_logging()
        else:
            is_active = app_state['logging_active']

        return jsonify({
            "logging": is_active,
            "status": "active" if is_active else "stopped"
        })
    except Exception as e:
        return jsonify({"logging": False, "status": "stopped"})

# ============= Data APIs =============
@app.route('/api/data/live/<int:channel>')
def api_live_data(channel):
    try:
        if 1 <= channel <= 8:
            if DATA_LOGGER_AVAILABLE:
                try:
                    temp = daq.get(channel) / 10.0
                    return jsonify({
                        "channel": channel,
                        "temperature": round(temp, 2),
                        "timestamp": datetime.now().isoformat()
                    })
                except:
                    pass

            # Simulated data with realistic variation
            base_temp = 20.0 + (channel * 5)
            variation = (time.time() % 60) * 0.3
            temp = base_temp + variation
            return jsonify({
                "channel": channel,
                "temperature": round(temp, 2),
                "timestamp": datetime.now().isoformat(),
                "simulated": True
            })
        else:
            return jsonify({"error": "Invalid channel"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/data/latest')
def api_latest_data():
    try:
        # Get latest readings from database (saved by logging thread)
        latest_readings = db_manager.get_latest_readings()

        print(f"[DEBUG] /api/data/latest called - Found {len(latest_readings) if latest_readings else 0} readings")
        if latest_readings:
            print(f"[DEBUG] Sample data: {latest_readings[0] if len(latest_readings) > 0 else 'None'}")

        if latest_readings and len(latest_readings) > 0:
            return jsonify(latest_readings)
        else:
            # No data in database yet - return empty array
            print("[DEBUG] Returning empty array - no data in database")
            return jsonify([])
    except Exception as e:
        print(f"[ERROR] /api/data/latest failed: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/data/historical')
def api_historical_data():
    try:
        hours = request.args.get('hours', 24, type=int)

        print(f"[DEBUG] /api/data/historical called - Requesting last {hours} hours")

        # Get real data from database using the database manager
        try:
            data = db_manager.get_historical_data(hours=hours)

            print(f"[DEBUG] /api/data/historical - Found {len(data) if data else 0} readings")
            if data and len(data) > 0:
                print(f"[DEBUG] Sample historical data: {data[0]}")
                return jsonify(data)
        except Exception as e:
            print(f"[ERROR] Database query failed: {e}")

        # No data available - return empty array (not simulated data)
        print("[DEBUG] Returning empty array - no historical data")
        return jsonify([])
    except Exception as e:
        print(f"[ERROR] /api/data/historical failed: {e}")
        return jsonify({"error": str(e)}), 500

# ============= Debug Endpoint =============
@app.route('/api/debug/database')
def api_debug_database():
    """Debug endpoint to check database contents"""
    try:
        # Get raw count
        cursor = db_manager.db.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM readings")
        total_count = cursor.fetchone()[0]

        # Get last 5 readings
        cursor.execute("SELECT * FROM readings ORDER BY id DESC LIMIT 5")
        recent = [dict(row) for row in cursor.fetchall()]

        # Get database file size
        import os
        db_path = db_manager.db.db_path if hasattr(db_manager.db, 'db_path') else 'datalogger.db'
        db_full_path = os.path.join(os.path.dirname(__file__), db_path)
        db_size_bytes = os.path.getsize(db_full_path) if os.path.exists(db_full_path) else 0
        db_size_mb = db_size_bytes / (1024 * 1024)
        db_size_kb = db_size_bytes / 1024

        # Get oldest and newest timestamps
        cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM readings")
        oldest, newest = cursor.fetchone()

        # Calculate data per channel
        cursor.execute("SELECT thermocouple_id, COUNT(*) FROM readings GROUP BY thermocouple_id ORDER BY thermocouple_id")
        channel_counts = {row[0]: row[1] for row in cursor.fetchall()}

        return jsonify({
            "total_readings": total_count,
            "db_size_bytes": db_size_bytes,
            "db_size_kb": round(db_size_kb, 2),
            "db_size_mb": round(db_size_mb, 2),
            "db_path": db_full_path,
            "oldest_reading": oldest,
            "newest_reading": newest,
            "channel_counts": channel_counts,
            "recent_readings": recent,
            "logging_active": is_logging() if DATA_LOGGER_AVAILABLE else False,
            "board_connected": is_connected() if DATA_LOGGER_AVAILABLE else False,
            "logging_interval_seconds": 5,
            "estimated_readings_per_hour": 8 * (3600 / 5),  # 8 channels * 720 readings/hour
            "estimated_readings_per_day": 8 * (3600 / 5) * 24
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============= System Status API =============
@app.route('/api/status')
def api_status():
    """Get current system status"""
    try:
        return jsonify({
            "board_connected": is_connected() if DATA_LOGGER_AVAILABLE else False,
            "logging_active": is_logging() if DATA_LOGGER_AVAILABLE else False,
            "board_info": get_board_info() if DATA_LOGGER_AVAILABLE else None
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============= System APIs =============
@app.route('/api/board_info')
def api_board_info():
    try:
        if DATA_LOGGER_AVAILABLE:
            return jsonify(get_board_info())
        else:
            return jsonify({
                "name": "Simulated 8-Thermocouple Board",
                "address": "0x16",
                "channels": 8,
                "status": "connected",
                "type": "K-type thermocouples",
                "simulated": True
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/system/cpu_temp')
def api_cpu_temp():
    try:
        if DATA_LOGGER_AVAILABLE:
            temp = get_cpu_temperature()
        else:
            temp = 45.5 + (time.time() % 10) * 0.5  # Simulated CPU temp

        return jsonify({"cpu_temperature": round(temp, 1)})
    except Exception as e:
        return jsonify({"cpu_temperature": 45.5, "simulated": True})

@app.route('/api/system/status')
def api_system_status():
    try:
        if DATA_LOGGER_AVAILABLE:
            logging_active = is_logging()
            daq_connected = is_connected()
            cpu_temp = get_cpu_temperature()
        else:
            logging_active = app_state['logging_active']
            daq_connected = app_state['daq_connected']
            cpu_temp = 45.5

        return jsonify({
            "logging": logging_active,
            "connected": daq_connected,
            "cpu_temp": round(cpu_temp, 1),
            "telegram_available": bool(app_state['telegram_token']),
            "uptime": str(datetime.now() - app_state['startup_time']).split('.')[0],
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "logging": app_state['logging_active'],
            "connected": app_state['daq_connected'],
            "cpu_temp": 45.5,
            "telegram_available": bool(app_state['telegram_token']),
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        })

# ============= Telegram Integration =============
@app.route('/api/telegram/send_test', methods=['POST'])
def api_telegram_test():
    try:
        message = request.json.get('message', 'Test message from DataLogger')
        success = send_telegram_message(message)
        return jsonify({
            "status": "sent" if success else "failed",
            "message": "Test message sent" if success else "Failed to send message"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/telegram/status')
def api_telegram_status():
    return jsonify({
        "available": bool(app_state['telegram_token']),
        "admin_users": len(app_state['admin_users']),
        "bot_username": "@eeng_datalogger_bot"
    })

# Simple webhook for Telegram commands
@app.route('/api/telegram/process_command', methods=['POST'])
def process_telegram_command():
    try:
        data = request.json
        command = data.get('command', '').lower().strip()
        chat_id = data.get('chat_id')

        if not command or not chat_id:
            return jsonify({"status": "error", "message": "Missing command or chat_id"})

        # Check authorization
        if chat_id not in app_state['admin_users']:
            send_telegram_message("Access Denied - Unauthorized user", chat_id)
            return jsonify({"status": "unauthorized"})

        # Process commands
        if command == '/start':
            response = """**Enertherm DataLogger**

Welcome! Remote temperature monitoring system.

**Commands:**
/status - System status
/temps - Current temperatures
/start_logging - Start logging
/stop_logging - Stop logging
/system - System info

Use these commands to control your DataLogger remotely!"""

            send_telegram_message(response, chat_id)

        elif command == '/status':
            logging_status = "Active" if app_state['logging_active'] else "Stopped"
            connection_status = "Connected" if app_state['daq_connected'] else "Disconnected"

            response = f"""**System Status**

Logging: {logging_status}
DAQ: {connection_status}
CPU: {api_cpu_temp().get_json()['cpu_temperature']}C
Uptime: {str(datetime.now() - app_state['startup_time']).split('.')[0]}"""

            send_telegram_message(response, chat_id)

        elif command == '/start_logging':
            result = api_start_logging().get_json()
            if result['status'] == 'started':
                send_telegram_message("**Logging Started** - Temperature data collection is now active", chat_id)
            else:
                send_telegram_message("**Failed to Start Logging**", chat_id)

        elif command == '/stop_logging':
            result = api_stop_logging().get_json()
            if result['status'] == 'stopped':
                send_telegram_message("**Logging Stopped** - Temperature data collection stopped", chat_id)
            else:
                send_telegram_message("**Failed to Stop Logging**", chat_id)

        elif command == '/temps':
            temp_data = api_latest_data().get_json()
            temp_lines = []

            for i in range(1, 9):
                channel_data = temp_data.get(f'thermocouple_{i}', {})
                temp = channel_data.get('temperature', 'N/A')
                if temp != 'N/A':
                    temp_lines.append(f"Ch{i}: {temp}C")

            response = "**Current Temperatures**\n\n" + "\n".join(temp_lines)
            send_telegram_message(response, chat_id)

        elif command == '/system':
            system_data = api_system_status().get_json()
            response = f"""**System Information**

Logging: {'Active' if system_data['logging'] else 'Stopped'}
Hardware: {'Connected' if system_data['connected'] else 'Disconnected'}
CPU Temperature: {system_data['cpu_temp']}C
Telegram: {'Available' if system_data['telegram_available'] else 'Unavailable'}
Uptime: {system_data.get('uptime', 'Unknown')}"""

            send_telegram_message(response, chat_id)

        else:
            send_telegram_message("Unknown command. Send /start for help.", chat_id)

        return jsonify({"status": "processed"})
    except Exception as e:
        print(f"Command processing error: {e}")
        return jsonify({"status": "error", "message": str(e)})

# Missing API endpoints that dashboard requires
@app.route('/api/gpio/status')
def api_gpio_status():
    """GPIO status endpoint - returns empty status (GPIO not implemented yet)"""
    return jsonify({
        "buttons": {},
        "leds": {},
        "available": False
    })

@app.route('/api/cpu_temperature')
def api_cpu_temperature_alt():
    """CPU temperature endpoint for dashboard compatibility"""
    try:
        result = get_cpu_temperature()
        cpu_temp = result.get("cpu_temp", 0)

        # Determine status based on temperature
        if cpu_temp < 0:
            status = "unavailable"
        elif cpu_temp >= 80:
            status = "critical"
        elif cpu_temp >= 70:
            status = "warning"
        else:
            status = "normal"

        return jsonify({
            "temperature": cpu_temp,
            "status": status
        })
    except Exception as e:
        return jsonify({"temperature": 0, "status": "error", "error": str(e)})

@app.route('/api/textfiles/stats')
def api_textfiles_stats():
    """Text file statistics endpoint"""
    return jsonify({
        "enabled": False,
        "files_count": 0,
        "total_size": 0
    })

@app.route('/api/notifications/status')
def api_notifications_status():
    """Notification status endpoint"""
    try:
        return jsonify({
            "enabled": notification_system.enabled if 'notification_system' in globals() else False,
            "email_configured": False,
            "sms_configured": False
        })
    except:
        return jsonify({"enabled": False})

@app.route('/api/notifications/config')
def api_notifications_config():
    """Notification configuration endpoint"""
    return jsonify({
        "email": {
            "enabled": False,
            "smtp_server": "",
            "smtp_port": 587,
            "from_address": "",
            "to_addresses": []
        },
        "sms": {
            "enabled": False
        },
        "alerts": {
            "high_temp_threshold": 80,
            "low_temp_threshold": 10
        }
    })

# ============= Database Configuration API =============
@app.route('/api/database/switch', methods=['POST'])
def api_database_switch():
    """Switch database configuration"""
    try:
        data = request.get_json()
        db_type = data.get('type', 'sqlite')
        config = data.get('config', {})

        # Build kwargs for switch_database
        kwargs = {}
        if db_type in ['postgresql', 'both']:
            if config.get('host'):
                kwargs['host'] = config['host']
            if config.get('port'):
                kwargs['port'] = int(config['port'])
            if config.get('database'):
                kwargs['database'] = config['database']
            if config.get('username'):
                kwargs['username'] = config['username']
            if config.get('password'):
                kwargs['password'] = config['password']

        # Switch database
        db_manager.switch_database(db_type, **kwargs)

        # Get connection status
        status = db_manager.get_connection_status()

        return jsonify({
            "success": True,
            "type": db_type,
            "info": status.get('info', {}),
            "message": f"Successfully switched to {db_type} database mode"
        })

    except Exception as e:
        print(f"[ERROR] Database switch failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/database/status')
def api_database_status():
    """Get current database status"""
    try:
        status = db_manager.get_connection_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============= Network Status API =============
@app.route('/api/network_status')
def api_network_status():
    """Get network and connectivity status"""
    try:
        import socket
        import time

        # Get local IP address
        local_ip = "Unknown"
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
        except:
            pass

        # Check internet connectivity
        internet_connected = False
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            internet_connected = True
        except:
            pass

        # Check if Telegram bot is active
        telegram_active = app_state.get('telegram_token') and TELEGRAM_BOT_AVAILABLE

        # Calculate uptime (if available from system start)
        uptime_seconds = None
        if 'start_time' in app_state:
            uptime_seconds = int(time.time() - app_state['start_time'])

        return jsonify({
            "local_ip": local_ip,
            "internet_connected": internet_connected,
            "telegram_active": telegram_active,
            "uptime_seconds": uptime_seconds,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        print(f"[ERROR] Network status check failed: {e}")
        return jsonify({
            "local_ip": "Unknown",
            "internet_connected": False,
            "telegram_active": False,
            "uptime_seconds": None,
            "error": str(e)
        })

# ============= Storage Info API =============
@app.route('/api/storage_info')
def api_storage_info():
    """API endpoint to show where data is stored - helps users find their files."""
    import os

    # Get absolute paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, 'datalogger.db')
    raw_path = os.path.join(base_dir, 'data', 'raw')
    daily_path = os.path.join(base_dir, 'data', 'daily')

    # Count files
    raw_files = 0
    daily_files = 0
    try:
        if os.path.exists(raw_path):
            raw_files = len([f for f in os.listdir(raw_path) if f.endswith('.txt')])
        if os.path.exists(daily_path):
            daily_files = len([f for f in os.listdir(daily_path) if f.endswith('.txt')])
    except:
        pass

    # Get database size
    db_size = os.path.getsize(db_path) if os.path.exists(db_path) else 0
    db_size_mb = round(db_size / (1024 * 1024), 2)

    # Get record count from database
    try:
        record_count = len(db_manager.get_historical_data(hours=24*365*10))
    except:
        record_count = 0

    return jsonify({
        "database": {
            "path": db_path,
            "size_bytes": db_size,
            "size_mb": db_size_mb,
            "record_count": record_count,
            "description": "Primary storage - All temperature readings"
        },
        "text_files": {
            "raw_path": str(raw_path),
            "daily_path": str(daily_path),
            "raw_file_count": raw_files,
            "daily_file_count": daily_files,
            "description": "Backup storage - Hourly and daily CSV files"
        },
        "how_data_is_saved": {
            "step1": "Temperature read from thermocouple sensor",
            "step2": "Calibration correction applied",
            "step3": "Saved to SQLite database (datalogger.db)",
            "step4": "Saved to text file (data/raw/YYYY-MM-DD_HH.txt)",
            "interval": "Every 5 seconds per channel"
        }
    })

@app.route('/api/storage_status')
def api_storage_status():
    """API endpoint to get storage/disk status."""
    import shutil
    base_dir = os.path.dirname(os.path.abspath(__file__))

    try:
        total, used, free = shutil.disk_usage(base_dir)
        return jsonify({
            "total_gb": round(total / (1024**3), 2),
            "used_gb": round(used / (1024**3), 2),
            "free_gb": round(free / (1024**3), 2),
            "percent_used": round((used / total) * 100, 1)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============= Version & Info API =============
@app.route('/api/version')
def api_version():
    """Get system version and copyright information"""
    return jsonify({
        "version": __version__,
        "build_date": "October 2025",
        "author": __author__,
        "copyright": __copyright__,
        "license": __license__,
        "product": "Temperature Data Logger System",
        "platform": platform.system(),
        "python_version": platform.python_version()
    })

if __name__ == '__main__':
    port = config.get('system.web_port', 8080)
    debug = config.get('system.debug_mode', False)

    print("=" * 70)
    print("    ENERTHERM ENGINEERING - TEMPERATURE DATA LOGGER SYSTEM")
    print(f"    Version {__version__} - {__copyright__}")
    print("=" * 70)
    print()

    try:
        # Initialize systems
        print("Initializing systems...")

        # Start notification system
        try:
            notification_system.start()
            print("+ Email notification system started")
        except Exception as e:
            print(f"- Email notifications failed: {e}")

        # Initialize DAQ connection
        try:
            if DATA_LOGGER_AVAILABLE and connect():
                app_state['daq_connected'] = True
                print("+ DAQ Hardware connected")
            else:
                print("- DAQ Hardware not found - using simulated data")
        except Exception as e:
            print(f"- DAQ connection failed: {e}")

        # Start Telegram bot
        telegram_bot = None
        if app_state['telegram_token'] and TELEGRAM_BOT_AVAILABLE:
            try:
                import data_logger
                telegram_bot = TelegramBot(data_logger_module=data_logger)
                if telegram_bot.start():
                    print("+ Telegram bot started successfully")
                    send_telegram_message("**DataLogger Started** - System is online and ready for monitoring")
                else:
                    print("- Failed to start Telegram bot")
            except Exception as e:
                print(f"- Telegram bot startup failed: {e}")
        elif app_state['telegram_token'] and TELEGRAM_AVAILABLE:
            # Fallback to simple notification mode
            try:
                url = f"https://api.telegram.org/bot{app_state['telegram_token']}/getMe"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    bot_data = response.json()
                    bot_username = bot_data['result']['username']
                    print(f"+ Telegram notifications active: @{bot_username}")
                    send_telegram_message("**DataLogger Started** - System is online (notifications only mode)")
                else:
                    print("- Telegram bot token invalid")
            except Exception as e:
                print(f"- Telegram test failed: {e}")
        else:
            print("- Telegram bot not configured")

        print()
        print("Access Points:")
        print(f"  Dashboard: http://localhost:{port}")
        if platform.system() != "Windows":
            print(f"  Network: http://your-pi-ip:{port}")
        print(f"  Telegram: @eeng_datalogger_bot")
        print()
        print("Starting web server...")
        print("=" * 60)

        app.run(host='0.0.0.0', port=port, debug=debug, threaded=True)

    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        try:
            if app_state['telegram_token']:
                send_telegram_message("**DataLogger Stopped** - System is shutting down")
            if telegram_bot:
                telegram_bot.stop()
            if DATA_LOGGER_AVAILABLE:
                stop_logging_thread()
            notification_system.stop()
            print("Cleanup completed")
        except Exception as e:
            print(f"Cleanup error: {e}")
