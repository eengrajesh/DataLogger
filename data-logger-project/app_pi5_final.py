#!/usr/bin/env python3
"""
Pi5 Final DataLogger - Windows and Linux compatible
Fixes all threading issues, graph display, and Telegram integration
"""

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
        get_cpu_temperature, is_logging, is_connected
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

# Application state
app_state = {
    'logging_active': False,
    'daq_connected': False,
    'telegram_token': config.get('telegram.bot_token', ''),
    'admin_users': config.get('telegram.admin_users', []),
    'startup_time': datetime.now()
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
                board_info = get_board_info()
                return jsonify({
                    "status": "success",
                    "board_info": board_info
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
        data = {}
        current_time = datetime.now().isoformat()
        
        for channel in range(1, 9):
            if DATA_LOGGER_AVAILABLE:
                try:
                    temp = daq.get(channel) / 10.0
                    data[f"thermocouple_{channel}"] = {
                        "temperature": round(temp, 2),
                        "timestamp": current_time
                    }
                    continue
                except:
                    pass
            
            # Simulated data
            base_temp = 20.0 + (channel * 4)
            variation = (time.time() % 30) * 0.4
            temp = base_temp + variation + (channel * 0.5)
            data[f"thermocouple_{channel}"] = {
                "temperature": round(temp, 2),
                "timestamp": current_time,
                "simulated": True
            }
        
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/data/historical')
def api_historical_data():
    try:
        hours = request.args.get('hours', 24, type=int)
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        # Try to get real data from database first
        try:
            query = """
            SELECT timestamp, thermocouple_id, temperature 
            FROM readings 
            WHERE timestamp >= ? AND timestamp <= ?
            ORDER BY timestamp
            """
            rows = db_manager.execute_query(query, (start_time.isoformat(), end_time.isoformat()))
            
            if rows and len(rows) > 10:  # If we have enough real data
                data = []
                for row in rows:
                    data.append({
                        "timestamp": row[0],
                        "thermocouple_id": row[1],
                        "temperature": row[2]
                    })
                return jsonify(data)
        except Exception as e:
            print(f"Database query failed: {e}")
        
        # Generate simulated historical data with realistic trends
        data = []
        current_time = start_time
        
        while current_time <= end_time:
            for channel in range(1, 9):
                # Create realistic temperature curves
                base_temp = 20.0 + (channel * 4)
                
                # Daily temperature cycle
                hour_of_day = current_time.hour
                daily_variation = 5 * abs(12 - hour_of_day) / 12
                
                # Long-term trend
                time_ratio = (current_time - start_time).total_seconds() / (hours * 3600)
                trend = 2 * time_ratio
                
                # Random variation
                random_variation = (current_time.timestamp() % 17) * 0.3
                
                temp = base_temp + daily_variation + trend + random_variation + (channel * 0.3)
                
                data.append({
                    "timestamp": current_time.isoformat(),
                    "thermocouple_id": channel,
                    "temperature": round(temp, 2),
                    "simulated": True
                })
            
            # Data point every 5 minutes
            current_time += timedelta(minutes=5)
        
        return jsonify(data)
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
    """Alternate CPU temperature endpoint for dashboard compatibility"""
    try:
        return jsonify(get_cpu_temperature())
    except:
        return jsonify({"cpu_temp": 0, "error": "Not available"})

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

if __name__ == '__main__':
    port = config.get('system.web_port', 8080)
    debug = config.get('system.debug_mode', False)
    
    print("=" * 60)
    print("    ENERTHERM DATALOGGER - Pi5 FINAL VERSION")
    print("=" * 60)
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