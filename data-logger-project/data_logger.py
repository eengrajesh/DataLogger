import time
import random
import threading
from database import add_reading, init_db

# --- Mock Hardware Section ---
# In a real environment, you would import the 'megaind' library here.
# For now, we simulate it to allow development without the hardware.
class MockMegaInd:
    def get_tc_temperature(self, channel):
        """Returns a simulated temperature reading."""
        # Simulate some baseline temperature with minor fluctuations
        base_temp = 25.0
        return base_temp + (channel * 0.5) + random.uniform(-0.2, 0.2)

# Instantiate the mock object. On the Pi, this would be the real library object.
megaind_hat = MockMegaInd()
# -----------------------------

# --- Configuration ---
NUMBER_OF_CHANNELS = 8
SAMPLE_INTERVAL_SECONDS = 5  # Read every 5 seconds

def log_temperatures():
    """
    This function runs in a loop to read temperatures from all channels
    and store them in the database.
    """
    print("Data logger thread started.")
    while True:
        try:
            for i in range(1, NUMBER_OF_CHANNELS + 1):
                # On the real hardware, this call would interact with the HAT
                temp = megaind_hat.get_tc_temperature(i)
                
                # Save the reading to the database
                add_reading(thermocouple_id=i, temperature=temp)
                
                print(f"Logged: Thermocouple {i}, Temperature: {temp:.2f}°C")
            
            # Wait for the next sample interval
            time.sleep(SAMPLE_INTERVAL_SECONDS)
            
        except Exception as e:
            print(f"An error occurred in the logger thread: {e}")
            # Wait a bit before retrying to avoid spamming errors
            time.sleep(10)

def start_logging_thread():
    """
    Initializes the database and starts the background thread for logging.
    """
    # Ensure the database is ready
    init_db()
    
    # Create and start the logging thread
    logging_thread = threading.Thread(target=log_temperatures, daemon=True)
    logging_thread.start()
    return logging_thread

if __name__ == '__main__':
    # This allows running the logger as a standalone script for testing
    print("Starting data logger as a standalone script...")
    start_logging_thread()
    
    # Keep the main thread alive to allow the daemon thread to run
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping data logger.")