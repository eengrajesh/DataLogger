import sm_tc
import time
import threading as th
import sys
import shutil
from datetime import datetime
from database_manager import DatabaseManager
from storage_manager import StorageManager
from text_file_logger import text_file_logger
from calibration import apply_correction
from config import config

# --- Hardware Section ---
daq = sm_tc.SMtc(0, 1)

# --- Database and Storage ---
db_manager = DatabaseManager()
storage_manager = StorageManager()

# --- Configuration ---
NUMBER_OF_CHANNELS = 8
SAMPLE_INTERVAL_SECONDS = config.get('logging.default_interval', 5)
sensor_intervals = {i: SAMPLE_INTERVAL_SECONDS for i in range(1, NUMBER_OF_CHANNELS + 1)}

# --- Logging Control ---
logging_thread = None
logging_stop_event = th.Event()
sensor_active_status = {i: True for i in range(1, NUMBER_OF_CHANNELS + 1)}

def get_board_info():
    return {"board_info": daq.get_board_info()}

def get_storage_status():
    total, used, free = shutil.disk_usage("/")
    return {"total": total, "used": used, "free": free}

def get_cpu_temperature():
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp = int(f.read()) / 1000.0
        return {"cpu_temp": temp}
    except FileNotFoundError:
        # Fallback for non-Pi environments for development/testing
        return {"cpu_temp": -1, "error": "Temperature sensor not found."}
    except Exception as e:
        return {"cpu_temp": -1, "error": str(e)}

def connect():
    return daq.connect()

def disconnect():
    daq.disconnect()

def set_sensor_status(channel, status):
    if channel in sensor_active_status:
        sensor_active_status[channel] = status
        print(f"Channel {channel} active status set to {status}")
        return True
    return False

def get_sensor_status():
    return sensor_active_status

def set_sensor_interval(channel, interval):
    if channel in sensor_intervals:
        sensor_intervals[channel] = int(interval)
        print(f"Channel {channel} interval set to {interval}s")
        return True
    return False

def get_sensor_intervals():
    return sensor_intervals

def log_temperatures():
    print("Data logger thread started.")
    last_log_time = {i: 0 for i in range(1, NUMBER_OF_CHANNELS + 1)}
    last_cleanup_time = time.time()

    while not logging_stop_event.is_set():
        try:
            current_time = time.time()
            for i in range(1, NUMBER_OF_CHANNELS + 1):
                if logging_stop_event.is_set():
                    break

                if sensor_active_status.get(i, False):
                    interval = sensor_intervals.get(i, SAMPLE_INTERVAL_SECONDS)
                    if current_time - last_log_time[i] >= interval:
                        temp = daq.get_temp(i)
                        if temp is not None:
                            corrected_temp = apply_correction(i, temp)
                            
                            # Log to text file first (faster, backup)
                            text_file_logger.log_reading(
                                channel=i, 
                                temperature=temp, 
                                calibrated_temp=corrected_temp,
                                timestamp=datetime.fromtimestamp(current_time)
                            )
                            
                            # Then log to database
                            db_manager.insert_reading(thermocouple_id=i, temperature=corrected_temp)
                            print(f"Logged: Ch {i}, Temp: {corrected_temp:.2f}°C, Int: {interval}s")
                            last_log_time[i] = current_time
                        else:
                            print(f"Failed to read temp for Ch {i}. Disabling.")
                            sensor_active_status[i] = False

            # Periodic maintenance (every hour)
            if current_time - last_cleanup_time > 3600:  # 1 hour
                try:
                    print("[DataLogger] Performing periodic maintenance...")
                    # Consolidate yesterday's data
                    text_file_logger.consolidate_daily_file()
                    # Clean up old files
                    text_file_logger.cleanup_old_files()
                    # Compress old files
                    text_file_logger.compress_old_files()
                    last_cleanup_time = current_time
                except Exception as e:
                    print(f"[DataLogger] Maintenance error: {e}")

            # Sleep for a short duration to prevent busy-waiting
            if not logging_stop_event.is_set():
                time.sleep(0.5)

        except Exception as e:
            print(f"An error occurred in the logger thread: {e}")
            time.sleep(10)
    print("Data logger thread has stopped.")

def start_logging_thread():
    global logging_thread
    if logging_thread is None or not logging_thread.is_alive():
        logging_stop_event.clear()
        logging_thread = th.Thread(target=log_temperatures, daemon=True)
        logging_thread.start()
        print("Logging thread initiated.")
        return True
    print("Logging thread is already running.")
    return False

def stop_logging_thread():
    global logging_thread
    if logging_thread is not None and logging_thread.is_alive():
        logging_stop_event.set()
        logging_thread.join()
        logging_thread = None
        print("Logging thread stopped.")
        return True
    print("Logging thread is not running or already stopped.")
    return False

def is_logging():
    """Check if logging thread is currently running"""
    global logging_thread
    return logging_thread is not None and logging_thread.is_alive()

def is_connected():
    """Check if DAQ hardware is connected"""
    return daq is not None and daq.connected

if __name__ == '__main__':
    print("Starting data logger as a standalone script...")
    start_logging_thread()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping data logger.")