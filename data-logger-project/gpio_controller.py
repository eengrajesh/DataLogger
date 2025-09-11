#!/usr/bin/env python3
"""
GPIO Controller for Enertherm DataLogger
Handles physical button inputs and LED status outputs
"""

import sys
import time
import threading
import json
from datetime import datetime
import logging

# Platform-specific GPIO handling
try:
    import RPi.GPIO as GPIO
    PLATFORM_PI = True
except ImportError:
    PLATFORM_PI = False

class MockGPIO:
    """Mock GPIO for development on non-Pi systems"""
    BCM = "BCM"
    IN = "IN" 
    OUT = "OUT"
    PUD_UP = "PUD_UP"
    RISING = "RISING"
    FALLING = "FALLING"
    HIGH = 1
    LOW = 0
    
    @staticmethod
    def setmode(mode): pass
    @staticmethod
    def setup(pin, mode, pull_up_down=None): pass
    @staticmethod
    def output(pin, state): pass
    @staticmethod
    def input(pin): return False
    @staticmethod
    def add_event_detect(pin, edge, callback=None, bouncetime=None): pass
    @staticmethod
    def cleanup(): pass

class GPIOController:
    """Controls physical GPIO buttons and LEDs for DataLogger"""
    
    # GPIO Pin assignments
    BUTTONS = {
        'START': 17,      # Green button - starts logging
        'SHUTDOWN': 27,   # Red button - stops logging/shutdown
        'EXPORT': 22,     # Blue button - export data
        'WIFI': 23        # Yellow button - wifi reset
    }
    
    LEDS = {
        'SYSTEM': 18,     # Green LED - system status
        'ERROR': 24,      # Red LED - error status  
        'NETWORK': 25,    # Blue LED - network status
        'LOGGING': 5      # Yellow LED - logging status
    }
    
    def __init__(self, data_logger_module=None, notification_system=None):
        """Initialize GPIO controller with optional data logger module reference"""
        self.data_logger_module = data_logger_module
        self.notification_system = notification_system
        self.gpio = GPIO if PLATFORM_PI else MockGPIO()
        self.running = False
        self.status_thread = None
        self.button_states = {}
        self.led_states = {}
        self.shutdown_timer = None
        
        # Setup logging
        self.logger = logging.getLogger('gpio_controller')
        self.logger.setLevel(logging.INFO)
        
        # Initialize GPIO
        self._setup_gpio()
        
    def _setup_gpio(self):
        """Initialize GPIO pins and event detection"""
        try:
            self.gpio.setmode(self.gpio.BCM)
            
            # Setup button pins (input with pull-up)
            for button, pin in self.BUTTONS.items():
                self.gpio.setup(pin, self.gpio.IN, pull_up_down=self.gpio.PUD_UP)
                self.button_states[button] = False
                
                # Add interrupt detection for button presses
                if PLATFORM_PI:
                    self.gpio.add_event_detect(
                        pin, 
                        self.gpio.FALLING,  # Button press (pull-up to ground)
                        callback=self._button_callback,
                        bouncetime=300  # 300ms debounce
                    )
            
            # Setup LED pins (output)
            for led, pin in self.LEDS.items():
                self.gpio.setup(pin, self.gpio.OUT)
                self.gpio.output(pin, self.gpio.LOW)
                self.led_states[led] = False
                
            self.logger.info("GPIO pins initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to setup GPIO: {e}")
            
    def _button_callback(self, channel):
        """Handle button press interrupts"""
        try:
            # Identify which button was pressed
            button_name = None
            for name, pin in self.BUTTONS.items():
                if pin == channel:
                    button_name = name
                    break
                    
            if button_name:
                self._handle_button_press(button_name)
                
        except Exception as e:
            self.logger.error(f"Button callback error: {e}")
            
    def _handle_button_press(self, button):
        """Process individual button press actions"""
        self.logger.info(f"{button} button pressed")
        
        try:
            if button == 'START':
                self._handle_start_button()
            elif button == 'SHUTDOWN':
                self._handle_shutdown_button()
            elif button == 'EXPORT':
                self._handle_export_button()
            elif button == 'WIFI':
                self._handle_wifi_button()
                
        except Exception as e:
            self.logger.error(f"Error handling {button} button: {e}")
            self.set_led('ERROR', True)
            
    def _handle_start_button(self):
        """Handle START button press - toggle logging"""
        if self.data_logger_module:
            if self.data_logger_module.is_logging():
                # Stop logging
                success = self.data_logger_module.stop_logging_thread()
                if success:
                    self.set_led('LOGGING', False)
                    self.logger.info("Logging stopped via START button")
                    
                    # Send notification
                    if self.notification_system:
                        self.notification_system.send_alert(
                            "system_stop",
                            "Data logging stopped via physical button",
                            "info"
                        )
                else:
                    self.set_led('ERROR', True)
            else:
                # Start logging
                success = self.data_logger_module.start_logging_thread()
                if success:
                    self.set_led('LOGGING', True)
                    self.set_led('ERROR', False)
                    self.logger.info("Logging started via START button")
                    
                    # Send notification
                    if self.notification_system:
                        self.notification_system.send_alert(
                            "system_start", 
                            "Data logging started via physical button",
                            "info"
                        )
                else:
                    self.set_led('ERROR', True)
                    self.logger.error("Failed to start logging via START button")
                    
    def _handle_shutdown_button(self):
        """Handle SHUTDOWN button - stop logging or system shutdown"""
        # First press stops logging
        if self.data_logger_module and self.data_logger_module.is_logging():
            self.data_logger_module.stop_logging_thread()
            self.set_led('LOGGING', False)
            self.logger.info("Logging stopped via SHUTDOWN button")
            return
            
        # Start shutdown timer for system shutdown
        if self.shutdown_timer is None:
            self.logger.info("Hold SHUTDOWN button for 5 seconds to shutdown system")
            self.set_led('ERROR', True)  # Indicate shutdown mode
            
            # Start 5-second timer
            self.shutdown_timer = threading.Timer(5.0, self._system_shutdown)
            self.shutdown_timer.start()
            
            # Check if button is still held after 5 seconds
            def check_shutdown():
                time.sleep(5.1)  # Slight delay after timer
                if not self.gpio.input(self.BUTTONS['SHUTDOWN']):  # Still pressed (LOW)
                    return  # Timer will handle shutdown
                else:
                    # Button released, cancel shutdown
                    if self.shutdown_timer:
                        self.shutdown_timer.cancel()
                        self.shutdown_timer = None
                    self.set_led('ERROR', False)
                    self.logger.info("System shutdown cancelled")
                    
            threading.Thread(target=check_shutdown, daemon=True).start()
            
    def _system_shutdown(self):
        """Perform system shutdown"""
        self.logger.info("Initiating system shutdown...")
        
        # Send shutdown notification
        if self.notification_system:
            self.notification_system.send_alert(
                "system_shutdown",
                "System shutdown initiated via physical button", 
                "critical"
            )
            
        # Flash all LEDs as shutdown indicator
        for i in range(5):
            for led in self.LEDS.keys():
                self.set_led(led, True)
            time.sleep(0.2)
            for led in self.LEDS.keys():
                self.set_led(led, False)
            time.sleep(0.2)
            
        # Cleanup and shutdown
        self.cleanup()
        
        if PLATFORM_PI:
            import os
            os.system("sudo shutdown -h now")
        else:
            self.logger.info("Mock shutdown (not on Pi)")
            
    def _handle_export_button(self):
        """Handle EXPORT button - export data to CSV"""
        self.logger.info("Exporting data via EXPORT button")
        self.set_led('NETWORK', True)  # Indicate export activity
        
        try:
            # Export data (implement based on your data export system)
            from datetime import datetime, timedelta
            import os
            
            # Create export directory if needed
            export_dir = "/data/exports" if PLATFORM_PI else "exports"
            os.makedirs(export_dir, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"datalogger_export_{timestamp}.csv"
            filepath = os.path.join(export_dir, filename)
            
            # Export last 24 hours of data
            success = self._export_data_to_csv(filepath)
            
            if success:
                self.logger.info(f"Data exported to {filepath}")
                # Flash network LED to indicate success
                for i in range(3):
                    self.set_led('NETWORK', False)
                    time.sleep(0.2)
                    self.set_led('NETWORK', True)
                    time.sleep(0.2)
            else:
                self.set_led('ERROR', True)
                self.logger.error("Data export failed")
                
        except Exception as e:
            self.logger.error(f"Export error: {e}")
            self.set_led('ERROR', True)
        finally:
            self.set_led('NETWORK', False)
            
    def _export_data_to_csv(self, filepath):
        """Export recent data to CSV file"""
        try:
            if self.data_logger_module and hasattr(self.data_logger_module, 'db_manager'):
                # Get last 24 hours of data
                end_time = datetime.now()
                start_time = end_time - timedelta(hours=24)
                
                # Query database for data
                query = """
                SELECT timestamp, thermocouple_id, temperature 
                FROM readings 
                WHERE timestamp >= ? AND timestamp <= ?
                ORDER BY timestamp
                """
                
                data = self.data_logger_module.db_manager.execute_query(
                    query, 
                    (start_time.isoformat(), end_time.isoformat())
                )
                
                # Write CSV
                with open(filepath, 'w') as f:
                    f.write("Timestamp,Channel,Temperature\n")
                    for row in data:
                        f.write(f"{row[0]},{row[1]},{row[2]}\n")
                        
                return True
                
        except Exception as e:
            self.logger.error(f"CSV export error: {e}")
            return False
            
        return False
        
    def _handle_wifi_button(self):
        """Handle WIFI button - reset wifi connection"""
        self.logger.info("WiFi reset via WIFI button")
        self.set_led('NETWORK', True)
        
        try:
            # Restart network interface (Pi-specific)
            if PLATFORM_PI:
                import subprocess
                
                # Restart wlan0 interface
                subprocess.run(["sudo", "ifdown", "wlan0"], capture_output=True)
                time.sleep(2)
                subprocess.run(["sudo", "ifup", "wlan0"], capture_output=True)
                
                self.logger.info("WiFi interface restarted")
                
                # Test connectivity after restart
                time.sleep(5)
                result = subprocess.run(["ping", "-c", "1", "8.8.8.8"], capture_output=True)
                if result.returncode == 0:
                    # Success - flash network LED
                    for i in range(3):
                        self.set_led('NETWORK', False)
                        time.sleep(0.3)
                        self.set_led('NETWORK', True)
                        time.sleep(0.3)
                else:
                    self.set_led('ERROR', True)
            else:
                self.logger.info("Mock WiFi restart (not on Pi)")
                
        except Exception as e:
            self.logger.error(f"WiFi reset error: {e}")
            self.set_led('ERROR', True)
        finally:
            self.set_led('NETWORK', False)
            
    def set_led(self, led_name, state):
        """Set LED on/off state"""
        if led_name in self.LEDS:
            pin = self.LEDS[led_name]
            self.gpio.output(pin, self.gpio.HIGH if state else self.gpio.LOW)
            self.led_states[led_name] = state
            
    def get_status(self):
        """Get current GPIO status for web interface"""
        return {
            'buttons': self.button_states.copy(),
            'leds': self.led_states.copy(),
            'platform': 'raspberry_pi' if PLATFORM_PI else 'development'
        }
        
    def start(self):
        """Start GPIO monitoring"""
        self.running = True
        
        # Start status monitoring thread
        self.status_thread = threading.Thread(target=self._status_monitor, daemon=True)
        self.status_thread.start()
        
        # Initialize system LED
        self.set_led('SYSTEM', True)
        self.logger.info("GPIO controller started")
        
    def _status_monitor(self):
        """Monitor system status and update LEDs accordingly"""
        while self.running:
            try:
                # Update button states (for web interface)
                for button, pin in self.BUTTONS.items():
                    self.button_states[button] = not self.gpio.input(pin)  # Inverted (pull-up)
                
                # Update system status LEDs
                if self.data_logger_module:
                    # Logging LED
                    self.set_led('LOGGING', self.data_logger_module.is_logging())
                    
                    # System LED (heartbeat)
                    if self.data_logger_module.is_connected():
                        self.set_led('SYSTEM', True)
                    else:
                        # Blink if disconnected
                        current = self.led_states.get('SYSTEM', False)
                        self.set_led('SYSTEM', not current)
                
                # Network status (basic connectivity check)
                if PLATFORM_PI and self.notification_system:
                    if hasattr(self.notification_system, 'connectivity_monitor'):
                        connected = self.notification_system.connectivity_monitor.is_internet_connected()
                        self.set_led('NETWORK', connected)
                
                time.sleep(1)  # Update every second
                
            except Exception as e:
                self.logger.error(f"Status monitor error: {e}")
                time.sleep(5)
                
    def stop(self):
        """Stop GPIO monitoring"""
        self.running = False
        
        if self.shutdown_timer:
            self.shutdown_timer.cancel()
            
        if self.status_thread:
            self.status_thread.join(timeout=2)
            
        self.logger.info("GPIO controller stopped")
        
    def cleanup(self):
        """Cleanup GPIO resources"""
        self.stop()
        
        # Turn off all LEDs
        for led in self.LEDS.keys():
            self.set_led(led, False)
            
        # Cleanup GPIO
        if PLATFORM_PI:
            self.gpio.cleanup()
            
        self.logger.info("GPIO cleanup completed")

# Test function for standalone operation
def test_gpio():
    """Test GPIO functionality standalone"""
    logging.basicConfig(level=logging.INFO)
    
    print("Testing GPIO Controller...")
    controller = GPIOController()
    
    try:
        controller.start()
        print("GPIO Controller started. Press buttons to test...")
        print("Press Ctrl+C to exit")
        
        # Test LED sequence
        leds = ['SYSTEM', 'ERROR', 'NETWORK', 'LOGGING']
        for led in leds:
            print(f"Testing {led} LED...")
            controller.set_led(led, True)
            time.sleep(1)
            controller.set_led(led, False)
            time.sleep(0.5)
            
        # Keep running to test buttons
        while True:
            status = controller.get_status()
            print(f"Status: {status}")
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        controller.cleanup()

if __name__ == "__main__":
    test_gpio()