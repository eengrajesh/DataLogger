#!/usr/bin/env python3
"""
Pi5 Ready DataLogger - Fixed version for Raspberry Pi deployment
Solves threading issues, graph display, and Telegram bot integration
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
import asyncio
import threading
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

# Simple Telegram bot without threading issues
try:
    from telegram import Bot
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("Telegram library not available")

app = Flask(__name__)
db_manager = DatabaseManager()
storage_manager = StorageManager()

# Application state
app_state = {
    'logging_active': False,
    'daq_connected': False,
    'telegram_bot': None,
    'admin_users': config.get('telegram.admin_users', []),
    'startup_time': datetime.now()
}

# Initialize Telegram bot (simple, no threading)
def init_telegram_bot():
    """Initialize Telegram bot without threading issues"""
    if not TELEGRAM_AVAILABLE:
        return None
        
    try:
        bot_token = config.get('telegram.bot_token', '')
        if bot_token:
            bot = Bot(token=bot_token)
            # Test the bot
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            me = loop.run_until_complete(bot.get_me())
            loop.close()
            print(f"✅ Telegram bot connected: @{me.username}")
            return bot
    except Exception as e:
        print(f"⚠️ Telegram bot initialization failed: {e}")
    return None

def send_telegram_alert(message, level="info"):
    """Send message to Telegram admin users"""
    if app_state['telegram_bot'] and app_state['admin_users']:
        emoji_map = {"info": "ℹ️", "warning": "⚠️", "error": "❌", "success": "✅"}
        emoji = emoji_map.get(level, "ℹ️")
        formatted_message = f"{emoji} {message}"
        
        for user_id in app_state['admin_users']:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(
                    app_state['telegram_bot'].send_message(
                        chat_id=user_id, 
                        text=formatted_message,
                        parse_mode='Markdown'
                    )
                )
                loop.close()
            except Exception as e:
                print(f"Failed to send Telegram message: {e}")

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
                send_telegram_alert("🔌 **DAQ Connected**\nHardware connection established", "success")
            return jsonify({"status": "connected" if result else "failed"})
        else:
            app_state['daq_connected'] = True
            return jsonify({"status": "connected", "simulated": True})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/disconnect', methods=['POST'])
def api_disconnect():
    try:
        if DATA_LOGGER_AVAILABLE:
            result = disconnect()
            app_state['daq_connected'] = False
            return jsonify({"status": "disconnected" if result else "failed"})
        else:
            app_state['daq_connected'] = False
            return jsonify({"status": "disconnected", "simulated": True})
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
                send_telegram_alert("▶️ **Logging Started**\nTemperature data collection is now active", "success")
        else:
            app_state['logging_active'] = True
            result = True
            send_telegram_alert("▶️ **Logging Started**\n(Simulated mode)", "success")
        
        return jsonify({
            "status": "started" if result else "failed",
            "message": "Logging started successfully" if result else "Failed to start logging"
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
                send_telegram_alert("⏹️ **Logging Stopped**\nTemperature data collection stopped", "warning")
        else:
            app_state['logging_active'] = False
            result = True
            send_telegram_alert("⏹️ **Logging Stopped**\n(Simulated mode)", "warning")
        
        return jsonify({
            "status": "stopped" if result else "failed",
            "message": "Logging stopped successfully" if result else "Failed to stop logging"
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
            "telegram_bot": app_state['telegram_bot'] is not None,
            "uptime": str(datetime.now() - app_state['startup_time']),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "logging": app_state['logging_active'],
            "connected": app_state['daq_connected'],
            "cpu_temp": 45.5,
            "telegram_bot": app_state['telegram_bot'] is not None,
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        })

# ============= Telegram Integration =============
@app.route('/api/telegram/send_test', methods=['POST'])
def api_telegram_test():
    try:
        message = request.json.get('message', 'Test message from DataLogger')
        send_telegram_alert(message, "info")
        return jsonify({"status": "sent", "message": "Test message sent"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/telegram/status')
def api_telegram_status():
    return jsonify({
        "bot_available": app_state['telegram_bot'] is not None,
        "admin_users": len(app_state['admin_users']),
        "bot_username": "@eeng_datalogger_bot"
    })

# Simple webhook for Telegram commands
@app.route('/api/telegram/webhook', methods=['POST'])
def telegram_webhook():
    try:
        if not app_state['telegram_bot']:
            return jsonify({"status": "bot_not_available"})
        
        update = request.get_json()
        
        if 'message' in update:
            message = update['message']
            chat_id = message['chat']['id']
            text = message.get('text', '').lower().strip()
            
            # Check authorization
            if chat_id not in app_state['admin_users']:
                send_telegram_alert("🔒 Access Denied", "error")
                return jsonify({"status": "unauthorized"})
            
            # Process commands
            if text == '/start':
                response = """🌡️ **Enertherm DataLogger**

Welcome! Remote temperature monitoring system.

**Commands:**
📊 `/status` - System status
🌡️ `/temps` - Current temperatures  
▶️ `/start_logging` - Start logging
⏹️ `/stop_logging` - Stop logging
📁 `/export` - Download data
🔧 `/system` - System info

Use these commands to control your DataLogger remotely!"""
                
                send_telegram_alert(response, "info")
                
            elif text == '/status':
                logging_status = "🟢 Active" if app_state['logging_active'] else "🔴 Stopped"
                connection_status = "🟢 Connected" if app_state['daq_connected'] else "🔴 Disconnected"
                
                response = f"""📊 **System Status**

🔄 **Logging:** {logging_status}
🔌 **DAQ:** {connection_status}
🌡️ **CPU:** {api_cpu_temp().get_json()['cpu_temperature']}°C
⏰ **Uptime:** {str(datetime.now() - app_state['startup_time']).split('.')[0]}"""
                
                send_telegram_alert(response, "info")
                
            elif text == '/start_logging':
                result = api_start_logging().get_json()
                if result['status'] == 'started':
                    send_telegram_alert("✅ **Logging Started**\nTemperature data collection is now active", "success")
                else:
                    send_telegram_alert("❌ **Failed to Start Logging**", "error")
                    
            elif text == '/stop_logging':
                result = api_stop_logging().get_json()
                if result['status'] == 'stopped':
                    send_telegram_alert("⏹️ **Logging Stopped**\nTemperature data collection stopped", "warning")
                else:
                    send_telegram_alert("❌ **Failed to Stop Logging**", "error")
                    
            elif text == '/temps':
                temp_data = api_latest_data().get_json()
                temp_lines = []
                
                for i in range(1, 9):
                    channel_data = temp_data.get(f'thermocouple_{i}', {})
                    temp = channel_data.get('temperature', 'N/A')
                    if temp != 'N/A':
                        temp_lines.append(f"📊 **Ch{i}:** {temp}°C")
                
                response = "🌡️ **Current Temperatures**\n\n" + "\n".join(temp_lines)
                send_telegram_alert(response, "info")
                
            elif text == '/system':
                system_data = api_system_status().get_json()
                response = f"""⚙️ **System Information**

🔄 **Logging:** {'Active' if system_data['logging'] else 'Stopped'}
🔌 **Hardware:** {'Connected' if system_data['connected'] else 'Disconnected'}
🌡️ **CPU Temperature:** {system_data['cpu_temp']}°C
🤖 **Telegram Bot:** {'Active' if system_data['telegram_bot'] else 'Inactive'}
⏰ **Uptime:** {system_data.get('uptime', 'Unknown')}"""
                
                send_telegram_alert(response, "info")
                
            else:
                send_telegram_alert("❓ Unknown command. Send `/start` for help.", "warning")
        
        return jsonify({"status": "ok"})
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    port = config.get('system.web_port', 8080)
    debug = config.get('system.debug_mode', False)
    
    print("=" * 60)
    print("    ENERTHERM DATALOGGER - Pi5 READY VERSION")
    print("=" * 60)
    print()
    
    try:
        # Initialize systems
        print("🔧 Initializing systems...")
        
        # Start notification system
        try:
            notification_system.start()
            print("✅ Email notification system started")
        except Exception as e:
            print(f"⚠️ Email notifications failed: {e}")
        
        # Initialize DAQ connection
        try:
            if DATA_LOGGER_AVAILABLE and connect():
                app_state['daq_connected'] = True
                print("✅ DAQ Hardware connected")
            else:
                print("⚠️ DAQ Hardware not found - using simulated data")
        except Exception as e:
            print(f"⚠️ DAQ connection failed: {e}")
        
        # Initialize Telegram bot
        app_state['telegram_bot'] = init_telegram_bot()
        if app_state['telegram_bot']:
            print("✅ Telegram bot ready for remote access")
        else:
            print("⚠️ Telegram bot not available")
        
        print()
        print("🌐 **Access Points:**")
        print(f"   • Dashboard: http://localhost:{port}")
        print(f"   • Network: http://your-pi-ip:{port}")
        print(f"   • Telegram: @eeng_datalogger_bot")
        print()
        
        if app_state['telegram_bot']:
            send_telegram_alert("🚀 **DataLogger Started**\nSystem is online and ready for monitoring", "success")
        
        print("🚀 Starting web server...")
        print("=" * 60)
        
        app.run(host='0.0.0.0', port=port, debug=debug, threaded=True)
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
    finally:
        try:
            if app_state['telegram_bot']:
                send_telegram_alert("⏹️ **DataLogger Stopped**\nSystem is shutting down", "warning")
            if DATA_LOGGER_AVAILABLE:
                stop_logging_thread()
            notification_system.stop()
            print("✅ Cleanup completed")
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")