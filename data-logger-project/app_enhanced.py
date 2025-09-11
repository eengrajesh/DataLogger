from flask import Flask, render_template, jsonify, request, send_file
from database_manager import DatabaseManager
from storage_manager import StorageManager
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

# Route to serve the enhanced dashboard
@app.route('/')
def index():
    return render_template('dashboard.html')

# Route to serve the original interface
@app.route('/classic')
def classic():
    return render_template('index.html')

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
    
    app.run(host='0.0.0.0', port=port, debug=debug)