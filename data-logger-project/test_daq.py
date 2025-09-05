import sm_tc
import time

# Test function to read from a single channel
def test_channel_one():
    """
    Connects to the DAQ and reads the temperature from channel 1.
    """
    try:
        # The sm_tc library is initialized automatically
        print("Reading from thermocouple channel 1...")
        
        # Read the temperature from stack level 0, channel 1
        temp = sm_tc.get_temp(0, 1)
        
        if temp is not None:
            print(f"Successfully read temperature: {temp:.2f}°C")
        else:
            print("Failed to read temperature. The channel may be open or faulty.")
            
    except Exception as e:
        print(f"An error occurred while trying to read from the DAQ: {e}")
        print("Please ensure the following:")
        print("1. The DAQ is properly connected to the Raspberry Pi.")
        print("2. The I2C interface is enabled on your Raspberry Pi (use 'sudo raspi-config').")
        print("3. The sm_tc library is correctly placed in the project directory.")

if __name__ == '__main__':
    test_channel_one()