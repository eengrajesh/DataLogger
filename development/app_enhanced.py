from flask import Flask, render_template, jsonify, request, send_file, send_from_directory
from database_manager import DatabaseManager
from storage_manager import StorageManager
from text_file_logger import text_file_logger
from notification_system import notification_system, AlertLevel
from gpio_controller import GPIOController
from telegram_bot import TelegramBot
from data_logger import (
    start_logging_thread, stop_logging_thread, daq, 
    get_board_info, connect, disconnect, 
    set_sensor_status, get_sensor_status, 
    set_sensor_interval, get_sensor_intervals, 
    get_cpu_temperature
)
from calibration import get_calibration_factors, set_calibration_factor
from config import config
import os
import signal
import csv
import json
import io
from datetime import datetime, timedelta

app = Flask(__name__)
db_manager = DatabaseManager()
storage_manager = StorageManager()

# Initialize GPIO controller and Telegram bot
gpio_controller = None
telegram_bot = None

# Create static directory if it doesn't exist
static_dir = os.path.join(os.path.dirname(__file__), 'static')
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

# Route to serve the enhanced dashboard
@app.route('/')
def index():
    return render_template('dashboard.html')

# Route to serve the original interface
@app.route('/classic')
def classic():
    return render_template('index.html')

# Route to serve static files (logo, etc.)
@app.route('/static/<path:filename>')
def serve_static(filename):
    static_path = os.path.join(os.path.dirname(__file__), 'static')
    return send_from_directory(static_path, filename)

# ============= Connection Management =============
@app.route('/api/connect', methods=['POST'])
def api_connect():
    try:
        connected = connect()
        board_info = get_board_info() if connected else None
        return jsonify({
            "connected": connected,
            "board_info": board_info
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/disconnect', methods=['POST'])
def api_disconnect():
    try:
        disconnect()
        return jsonify({"disconnected": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============= Database Management =============
@app.route('/api/database/status')
def api_database_status():
    try:
        status = db_manager.get_connection_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/database/switch', methods=['POST'])
def api_switch_database():
    try:
        data = request.json
        db_type = data.get('type', 'sqlite')
        db_config = data.get('config', {})
        
        db_manager.switch_database(db_type, **db_config)
        status = db_manager.get_connection_status()
        
        return jsonify({
            "success": True,
            "type": db_type,
            "info": status['info']
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ============= Storage Management =============
@app.route('/api/storage/status')
def api_storage_status():
    try:
        status = storage_manager.get_storage_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/storage/devices')
def api_storage_devices():
    try:
        devices = storage_manager.scan_storage_devices()
        return jsonify([d.to_dict() for d in devices])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/storage/set', methods=['POST'])
def api_set_storage():
    try:
        data = request.json
        storage_type = data.get('type', 'local')
        success = storage_manager.set_active_storage(storage_type)
        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============= Data Operations =============
@app.route('/api/data/live/<int:channel>')
def api_live_data(channel):
    try:
        temp = daq.get_temp(channel)
        if temp is not None:
            return jsonify({
                "thermocouple_id": channel, 
                "temperature": temp,
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({"error": "Failed to read temperature"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/data/latest')
def api_latest_data():
    try:
        readings = db_manager.get_latest_readings()
        return jsonify(readings)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/data/historical')
def api_historical_data():
    try:
        hours = request.args.get('hours', 24, type=int)
        readings = db_manager.get_historical_data(hours=hours)
        return jsonify(readings)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/data/range')
def api_data_by_range():
    try:
        start = request.args.get('start')
        end = request.args.get('end')
        channel = request.args.get('channel', type=int)
        
        if not start or not end:
            return jsonify({"error": "Start and end dates required"}), 400
        
        start_date = datetime.fromisoformat(start)
        end_date = datetime.fromisoformat(end)
        
        readings = db_manager.get_data_by_range(start_date, end_date, channel)
        return jsonify(readings)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/data/export/<format>')
def api_export_data(format):
    try:
        start = request.args.get('start')
        end = request.args.get('end')
        
        if start and end:
            start_date = datetime.fromisoformat(start)
            end_date = datetime.fromisoformat(end)
            data = db_manager.get_data_by_range(start_date, end_date)
        else:
            data = db_manager.get_historical_data(hours=24)
        
        if format == 'csv':
            output = io.StringIO()
            if data:
                writer = csv.DictWriter(output, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            
            output.seek(0)
            return send_file(
                io.BytesIO(output.getvalue().encode()),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'datalog_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            )
        
        elif format == 'json':
            return send_file(
                io.BytesIO(json.dumps(data, indent=2, default=str).encode()),
                mimetype='application/json',
                as_attachment=True,
                download_name=f'datalog_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            )
        
        else:
            return jsonify({"error": "Invalid format. Use 'csv' or 'json'"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/data/clear', methods=['POST'])
def api_clear_data():
    try:
        db_manager.clear_all_data()
        return jsonify({"status": "success", "message": "All data cleared."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============= Text File Data Operations =============
@app.route('/api/textfiles/export_csv', methods=['POST'])
def api_export_csv_from_textfiles():
    """Generate CSV export from text files with filtering options"""
    try:
        data = request.get_json()
        
        # Parse parameters
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        channels = data.get('channels', [])  # List of channel numbers
        include_raw = data.get('include_raw', False)
        
        if not start_date_str or not end_date_str:
            return jsonify({"error": "start_date and end_date are required"}), 400
        
        start_date = datetime.fromisoformat(start_date_str)
        end_date = datetime.fromisoformat(end_date_str)
        
        # Generate CSV export
        export_path = text_file_logger.generate_csv_export(
            start_date, end_date, channels if channels else None, include_raw
        )
        
        if export_path:
            return send_file(
                export_path,
                as_attachment=True,
                download_name=f'temperature_data_{start_date.strftime("%Y%m%d")}_{end_date.strftime("%Y%m%d")}.csv',
                mimetype='text/csv'
            )
        else:
            return jsonify({"error": "Failed to generate CSV export"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/textfiles/data_range', methods=['POST'])
def api_get_textfile_data_range():
    """Get data from text files for a specific date range"""
    try:
        data = request.get_json()
        
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        channels = data.get('channels', None)
        
        if not start_date_str or not end_date_str:
            return jsonify({"error": "start_date and end_date are required"}), 400
        
        start_date = datetime.fromisoformat(start_date_str)
        end_date = datetime.fromisoformat(end_date_str)
        
        readings = text_file_logger.get_readings_by_date_range(start_date, end_date, channels)
        
        # Convert datetime objects to strings for JSON serialization
        for reading in readings:
            reading['timestamp'] = reading['timestamp'].isoformat()
        
        return jsonify({
            "readings": readings,
            "count": len(readings),
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/textfiles/stats')
def api_textfile_storage_stats():
    """Get statistics about text file storage"""
    try:
        stats = text_file_logger.get_storage_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/textfiles/maintenance', methods=['POST'])
def api_textfile_maintenance():
    """Manually trigger text file maintenance operations"""
    try:
        operation = request.json.get('operation', 'all')
        
        results = {"operations": []}
        
        if operation in ['all', 'consolidate']:
            try:
                text_file_logger.consolidate_daily_file()
                results["operations"].append({"consolidate": "success"})
            except Exception as e:
                results["operations"].append({"consolidate": f"error: {e}"})
        
        if operation in ['all', 'cleanup']:
            try:
                text_file_logger.cleanup_old_files()
                results["operations"].append({"cleanup": "success"})
            except Exception as e:
                results["operations"].append({"cleanup": f"error: {e}"})
        
        if operation in ['all', 'compress']:
            try:
                text_file_logger.compress_old_files()
                results["operations"].append({"compress": "success"})
            except Exception as e:
                results["operations"].append({"compress": f"error: {e}"})
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============= Logging Control =============
@app.route('/api/logging/start', methods=['POST'])
def api_start_logging():
    try:
        if start_logging_thread():
            return jsonify({"status": "started", "message": "Logging started."})
        else:
            return jsonify({"status": "already_running", "message": "Logging already running."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/logging/stop', methods=['POST'])
def api_stop_logging():
    try:
        if stop_logging_thread():
            return jsonify({"status": "stopped", "message": "Logging stopped."})
        else:
            return jsonify({"status": "not_running", "message": "Logging not running."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/logging/status')
def api_logging_status():
    try:
        from data_logger import logging_thread
        is_running = logging_thread is not None and logging_thread.is_alive()
        active_sensors = sum(1 for v in get_sensor_status().values() if v)
        
        return jsonify({
            "running": is_running,
            "active_channels": active_sensors,
            "total_channels": 8
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============= Sensor Configuration =============
@app.route('/api/sensor_status/<int:channel>', methods=['GET', 'POST'])
def api_sensor_status(channel):
    try:
        if request.method == 'POST':
            data = request.json
            active = data.get('active', True)
            success = set_sensor_status(channel, active)
            return jsonify({"success": success, "channel": channel, "active": active})
        else:
            status = get_sensor_status()
            return jsonify({"channel": channel, "active": status.get(channel, False)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sensor_interval/<int:channel>', methods=['GET', 'POST'])
def api_sensor_interval(channel):
    try:
        if request.method == 'POST':
            data = request.json
            interval = data.get('interval', 5)
            success = set_sensor_interval(channel, interval)
            return jsonify({"success": success, "channel": channel, "interval": interval})
        else:
            intervals = get_sensor_intervals()
            return jsonify({"channel": channel, "interval": intervals.get(channel, 5)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sensors/status')
def api_all_sensors_status():
    try:
        return jsonify({
            "status": get_sensor_status(),
            "intervals": get_sensor_intervals()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============= Calibration =============
@app.route('/api/calibration')
def api_get_calibration():
    try:
        factors = get_calibration_factors()
        return jsonify(factors)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/calibration/<int:channel>', methods=['POST'])
def api_set_calibration(channel):
    try:
        data = request.json
        factor = data.get('factor', 0.0)
        set_calibration_factor(channel, factor)
        return jsonify({"success": True, "channel": channel, "factor": factor})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============= System Information =============
@app.route('/api/board_info')
def api_board_info():
    try:
        info = get_board_info()
        return jsonify(info)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/system/status')
def api_system_status():
    try:
        cpu_temp = get_cpu_temperature()
        storage_status = storage_manager.get_storage_status()
        db_status = db_manager.get_connection_status()
        
        from data_logger import logging_thread
        logging_status = logging_thread is not None and logging_thread.is_alive()
        
        return jsonify({
            "cpu_temperature": cpu_temp,
            "storage": storage_status,
            "database": db_status,
            "logging_active": logging_status,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/cpu_temperature')
def api_cpu_temperature():
    try:
        cpu_temp_data = get_cpu_temperature()
        temp = cpu_temp_data.get('cpu_temp', -1)
        
        # Define temperature thresholds
        warning_threshold = 70
        critical_threshold = 80
        
        status = "normal"
        if temp > 0:
            if temp >= critical_threshold:
                status = "critical"
            elif temp >= warning_threshold:
                status = "warning"
        else:
            status = "unavailable"
            
        return jsonify({
            "temperature": temp,
            "status": status,
            "warning_threshold": warning_threshold,
            "critical_threshold": critical_threshold,
            "unit": "°C"
        })
    except Exception as e:
        return jsonify({"error": str(e), "temperature": -1, "status": "error"}), 500

@app.route('/api/config')
def api_get_config():
    try:
        return jsonify(config.config)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/config', methods=['POST'])
def api_update_config():
    try:
        data = request.json
        for key, value in data.items():
            config.set(key, value)
        return jsonify({"success": True, "config": config.config})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============= Email Notification System =============
@app.route('/api/notifications/config')
def api_get_notification_config():
    """Get current notification configuration"""
    try:
        return jsonify(notification_system.config)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/notifications/config', methods=['POST'])
def api_update_notification_config():
    """Update notification configuration"""
    try:
        new_config = request.get_json()
        notification_system.update_config(new_config)
        return jsonify({"status": "success", "message": "Configuration updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/notifications/test', methods=['POST'])
def api_test_notifications():
    """Send a test email notification"""
    try:
        data = request.get_json() or {}
        recipient = data.get('recipient')
        
        if notification_system.test_email(recipient):
            return jsonify({"status": "success", "message": "Test email sent successfully"})
        else:
            return jsonify({"status": "error", "message": "Failed to send test email"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/notifications/start', methods=['POST'])
def api_start_notifications():
    """Start the notification system"""
    try:
        if notification_system.start():
            return jsonify({"status": "success", "message": "Notification system started"})
        else:
            return jsonify({"status": "info", "message": "Notification system already running"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/notifications/stop', methods=['POST'])
def api_stop_notifications():
    """Stop the notification system"""
    try:
        notification_system.stop()
        return jsonify({"status": "success", "message": "Notification system stopped"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/notifications/status')
def api_notification_status():
    """Get notification system status"""
    try:
        connectivity = notification_system.connectivity.get_connectivity_status()
        return jsonify({
            "running": notification_system.is_running,
            "enabled": notification_system.config['enabled'],
            "connectivity": connectivity,
            "queue_size": notification_system.alert_queue.qsize(),
            "sent_alerts_count": len(notification_system.sent_alerts),
            "last_cpu_temp": notification_system.last_cpu_temp,
            "last_disk_usage": notification_system.last_disk_usage
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/notifications/alert', methods=['POST'])
def api_create_alert():
    """Create a custom alert"""
    try:
        data = request.get_json()
        level = AlertLevel(data.get('level', 'info'))
        title = data.get('title', 'Custom Alert')
        message = data.get('message', 'No message provided')
        alert_data = data.get('data', {})
        
        alert = notification_system.create_alert(level, title, message, alert_data)
        
        return jsonify({
            "status": "success",
            "message": "Alert created",
            "alert_id": str(hash(f"{alert.title}{alert.timestamp}"))
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============= GPIO Control =============
@app.route('/api/gpio/status', methods=['GET'])
def api_gpio_status():
    """Get current GPIO button and LED status"""
    try:
        if gpio_controller:
            return jsonify(gpio_controller.get_status())
        else:
            return jsonify({
                "buttons": {"START": False, "SHUTDOWN": False, "EXPORT": False, "WIFI": False},
                "leds": {"SYSTEM": False, "ERROR": False, "NETWORK": False, "LOGGING": False},
                "platform": "not_initialized"
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/gpio/led/<led_name>/<state>', methods=['POST'])
def api_gpio_led_control(led_name, state):
    """Manually control LED state (for testing)"""
    try:
        if gpio_controller and led_name.upper() in ['SYSTEM', 'ERROR', 'NETWORK', 'LOGGING']:
            led_state = state.lower() in ['true', '1', 'on']
            gpio_controller.set_led(led_name.upper(), led_state)
            return jsonify({"status": f"{led_name} LED set to {led_state}"})
        else:
            return jsonify({"error": "GPIO controller not available or invalid LED"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============= System Control =============
@app.route('/api/system/restart', methods=['POST'])
def api_restart_system():
    try:
        if os.name != 'nt':  # Not Windows
            os.system('sudo reboot')
            return jsonify({"status": "restarting"})
        else:
            return jsonify({"error": "Restart not supported on Windows"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/system/shutdown', methods=['POST'])
def api_shutdown_system():
    try:
        if os.name != 'nt':  # Not Windows
            os.system('sudo shutdown -h now')
            return jsonify({"status": "shutting down"})
        else:
            return jsonify({"error": "Shutdown not supported on Windows"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = config.get('system.web_port', 8080)
    debug = config.get('system.debug_mode', False)
    
    print(f"Starting DataLogger Web Interface on port {port}")
    print(f"Access the dashboard at: http://localhost:{port}")
    print(f"Access the classic interface at: http://localhost:{port}/classic")
    
    try:
        # Start notification system
        notification_system.start()
        print("Email notification system started")
        
        # Initialize and start GPIO controller
        try:
            # Import data_logger module to pass to GPIO controller
            import data_logger
            
            gpio_controller = GPIOController(
                data_logger_module=data_logger,
                notification_system=notification_system
            )
            gpio_controller.start()
            print("GPIO controller started - physical buttons active")
        except Exception as e:
            print(f"GPIO controller failed to start: {e}")
            print("Running without physical button support")
        
        # Initialize and start Telegram bot
        try:
            telegram_bot = TelegramBot(
                data_logger_module=data_logger,
                notification_system=notification_system,
                gpio_controller=gpio_controller
            )
            
            if telegram_bot.start():
                print("Telegram bot started - remote access enabled")
                print("Send /start to your bot to begin using it")
            else:
                print("Telegram bot failed to start - check configuration")
                print("Edit config.py to add your bot token and user ID")
                
        except Exception as e:
            print(f"Telegram bot initialization failed: {e}")
            print("Running without Telegram bot support")
        
        app.run(host='0.0.0.0', port=port, debug=debug)
        
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        # Cleanup
        try:
            if telegram_bot:
                telegram_bot.stop()
                print("Telegram bot stopped")
            if gpio_controller:
                gpio_controller.cleanup()
                print("GPIO controller cleaned up")
            notification_system.stop()
            stop_logging_thread()
            print("Cleanup completed")
        except Exception as e:
            print(f"Cleanup error: {e}")