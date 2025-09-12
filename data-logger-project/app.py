from flask import Flask, render_template, jsonify, send_from_directory
from database import get_latest_readings, get_historical_data, get_average_temperatures, clear_all_data, get_all_data
from data_logger import start_logging_thread, stop_logging_thread, daq, get_board_info, connect, disconnect, get_storage_status, set_sensor_status, get_sensor_status, set_sensor_interval, get_sensor_intervals, get_cpu_temperature
from calibration import get_calibration_factors, set_calibration_factor
import os
import signal

app = Flask(__name__)

# Create static directory
static_dir = os.path.join(os.path.dirname(__file__), 'static')
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

@app.route('/static/<path:filename>')
def serve_static(filename):
    static_path = os.path.join(os.path.dirname(__file__), 'static')
    return send_from_directory(static_path, filename)

@app.route('/api/data/live/<int:channel>')
def api_live_data(channel):
    """API endpoint to get a live reading from a specific channel."""
    try:
        # Check if board is connected before reading temperature
        if not daq.connected:
            return jsonify({"error": "Board not connected"}), 503
        
        temp = daq.get_temp(channel)
        if temp is not None:
            return jsonify({"thermocouple_id": channel, "temperature": temp})
        else:
            return jsonify({"error": "Failed to read temperature"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    """Serves the main dashboard page."""
    return render_template('dashboard.html')

@app.route('/classic')
def classic():
    """Serves the classic interface."""
    return render_template('index.html')

@app.route('/api/data/latest')
def api_latest_data():
    """API endpoint to get the latest reading for each thermocouple."""
    try:
        readings = get_latest_readings()
        return jsonify(readings)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/data/historical')
def api_historical_data():
    """API endpoint to get historical data for the charts."""
    try:
        readings = get_historical_data(hours=24)
        return jsonify(readings)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/logging/start', methods=['POST'])
def api_start_logging():
    """API endpoint to start the data logging."""
    if start_logging_thread():
        return jsonify({"status": "success", "message": "Logging started."})
    else:
        return jsonify({"status": "error", "message": "Logging was already running."})

@app.route('/api/logging/stop', methods=['POST'])
def api_stop_logging():
    """API endpoint to stop the data logging."""
    if stop_logging_thread():
        return jsonify({"status": "success", "message": "Logging stopped."})
    else:
        return jsonify({"status": "error", "message": "Logging was not running."})

@app.route('/api/connect', methods=['POST'])
def api_connect():
    """API endpoint to connect to the SMTC board."""
    if connect():
        board_info = get_board_info()
        return jsonify({"status": "success", "message": "Successfully connected to SMTC.", "board_info": board_info})
    else:
        return jsonify({"status": "error", "message": "Could not connect to SMTC."})

@app.route('/api/disconnect', methods=['POST'])
def api_disconnect():
    """API endpoint to disconnect from the SMTC board."""
    disconnect()
    board_info = get_board_info()
    return jsonify({"status": "success", "message": "Successfully disconnected from SMTC.", "board_info": board_info})

@app.route('/api/board_info')
def api_board_info():
    """API endpoint to get the board info."""
    return jsonify(get_board_info())

@app.route('/api/storage_status')
def api_storage_status():
    """API endpoint to get the storage status."""
    return jsonify(get_storage_status())

@app.route('/api/cpu_temp')
def api_cpu_temp():
    """API endpoint to get the CPU temperature."""
    return jsonify(get_cpu_temperature())

@app.route('/api/data/clear', methods=['POST'])
def api_clear_data():
    """API endpoint to clear all data from the database."""
    try:
        clear_all_data()
        return jsonify({"status": "success", "message": "All data cleared."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/data/download/<string:file_format>')
def api_download_data(file_format):
    """API endpoint to download all data in a specified format."""
    try:
        from flask import Response
        import json
        import io
        import csv

        readings = get_all_data()

        if not readings:
            return Response(
                "No data to download.",
                mimetype="text/plain",
                headers={"Content-Disposition": "attachment;filename=error.txt"}
            )

        if file_format == 'json':
            for reading in readings:
                reading['timestamp'] = reading['timestamp'].isoformat()
            
            output = json.dumps(readings, indent=4)
            return Response(
                output,
                mimetype="application/json",
                headers={"Content-Disposition": "attachment;filename=readings.json"}
            )
        elif file_format == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)
            
            if readings:
                writer.writerow(readings[0].keys())
            
            for reading in readings:
                writer.writerow(reading.values())
            
            return Response(
                output.getvalue(),
                mimetype="text/csv",
                headers={"Content-Disposition": "attachment;filename=readings.csv"}
            )
        else:
            return jsonify({"status": "error", "message": "Invalid file format."}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/data/average')
def api_average_data():
    """API endpoint to get the average temperature for each thermocouple."""
    try:
        avg_temps = get_average_temperatures()
        return jsonify(avg_temps)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/sensor_type/<int:channel>', methods=['POST'])
def api_set_sensor_type(channel):
    """API endpoint to set the sensor type for a specific channel."""
    try:
        from flask import request
        sensor_type = request.json.get('sensor_type')
        daq.set_sensor_type(channel, sensor_type)
        return jsonify({"status": "success", "message": f"Sensor type for channel {channel} set to {sensor_type}."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/sensor_status/<int:channel>', methods=['POST'])
def api_set_sensor_status(channel):
    """API endpoint to set the active status of a sensor."""
    try:
        from flask import request
        status = request.json.get('status')
        if set_sensor_status(channel, status):
            return jsonify({"status": "success", "message": f"Sensor status for channel {channel} set to {status}."})
        else:
            return jsonify({"status": "error", "message": "Invalid channel."}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/sensor_status')
def api_get_sensor_status():
    """API endpoint to get the active status of all sensors."""
    try:
        return jsonify(get_sensor_status())
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/sensor_interval/<int:channel>', methods=['POST'])
def api_set_sensor_interval(channel):
    """API endpoint to set the sampling interval for a sensor."""
    try:
        from flask import request
        interval = request.json.get('interval')
        if set_sensor_interval(channel, interval):
            return jsonify({"status": "success", "message": f"Interval for channel {channel} set to {interval}s."})
        else:
            return jsonify({"status": "error", "message": "Invalid channel."}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/sensor_intervals')
def api_get_sensor_intervals():
    """API endpoint to get the sampling intervals of all sensors."""
    try:
        return jsonify(get_sensor_intervals())
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/system/restart', methods=['POST'])
def api_restart_pi():
    """API endpoint to restart the Raspberry Pi."""
    try:
        os.system('sudo reboot')
        return jsonify({"status": "success", "message": "Raspberry Pi is restarting."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/sensor/reset', methods=['POST'])
def api_reset_board():
    """API endpoint to reset the sensor board."""
    try:
        disconnect()
        connect()
        return jsonify({"status": "success", "message": "Sensor board has been reset."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/calibration', methods=['GET'])
def api_get_calibration():
    """API endpoint to get the current calibration factors."""
    try:
        return jsonify(get_calibration_factors())
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/calibration/<int:channel>', methods=['POST'])
def api_set_calibration(channel):
    """API endpoint to set a calibration factor for a specific channel."""
    try:
        from flask import request
        factor = request.json.get('factor')
        set_calibration_factor(channel, factor)
        return jsonify({"status": "success", "message": f"Calibration factor for channel {channel} set to {factor}."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/system/status')
def api_system_status():
    """API endpoint for system status - required by dashboard.html"""
    try:
        from datetime import datetime
        
        # Get system status
        logging_active = False
        daq_connected = daq.connected if daq else False
        
        try:
            from data_logger import is_logging
            logging_active = is_logging()
        except:
            pass
            
        try:
            cpu_info = get_cpu_temperature()
            cpu_temp = cpu_info.get('cpu_temp', 45.5) if isinstance(cpu_info, dict) else 45.5
        except:
            cpu_temp = 45.5
        
        return jsonify({
            "logging": logging_active,
            "connected": daq_connected,
            "cpu_temp": round(cpu_temp, 1),
            "telegram_available": False,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "logging": False,
            "connected": False,
            "cpu_temp": 45.5,
            "telegram_available": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)