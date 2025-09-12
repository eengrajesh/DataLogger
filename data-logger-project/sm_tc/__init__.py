import struct
import platform
import random
import time

# Check if running on a non-Linux platform (like Windows or macOS)
IS_WINDOWS = platform.system() == "Windows"

if not IS_WINDOWS:
    import smbus2

__version__ = "1.0.2"
_CARD_BASE_ADDRESS = 0x16
_STACK_LEVEL_MAX = 7
_IN_CH_COUNT = 8
_TEMP_SIZE_BYTES = 2
_TEMP_SCALE_FACTOR = 10.0

_TCP_VAL1_ADD = 0
_TCP_TYPE1_ADD = 16
_REVISION_HW_MAJOR_MEM_ADD = 47
_REVISION_HW_MINOR_MEM_ADD = 48

_TC_TYPE_B = 0
_TC_TYPE_E = 1
_TC_TYPE_J = 2
_TC_TYPE_K = 3
_TC_TYPE_N = 4
_TC_TYPE_R = 5
_TC_TYPE_S = 6
_TC_TYPE_T = 7

_TC_TYPES = ['B', 'E', 'J', 'K', 'N', 'R', 'S', 'T']

class MockSMtc:
    def __init__(self, stack=0, i2c=1):
        self._card_rev_major = 1
        self._card_rev_minor = 0
        self.connected = False
        self._sensor_types = {i: _TC_TYPE_K for i in range(1, _IN_CH_COUNT + 1)}

    def connect(self):
        print("MockSMtc: Connecting...")
        time.sleep(0.5) # Simulate connection time
        self.connected = True
        print("MockSMtc: Successfully connected to mock board.")
        return True

    def disconnect(self):
        self.connected = False
        print("MockSMtc: Disconnected from mock board.")

    def get_board_info(self):
        return {
            "connected": self.connected,
            "hw_rev_major": self._card_rev_major,
            "hw_rev_minor": self._card_rev_minor,
        }

    def set_sensor_type(self, channel, cfg):
        if not self.connected:
            return
        if 1 <= channel <= _IN_CH_COUNT and _TC_TYPE_B <= cfg <= _TC_TYPE_T:
            self._sensor_types[channel] = cfg
            print(f"MockSMtc: Set sensor type for channel {channel} to {_TC_TYPES[cfg]}")
        else:
            raise ValueError("Invalid channel or thermocouple type.")

    def get_sensor_type(self, channel):
        if not self.connected:
            return None
        if 1 <= channel <= _IN_CH_COUNT:
            return self._sensor_types.get(channel)
        raise ValueError("Invalid input channel number.")

    def get_temp(self, channel):
        # Only return temperature if connected
        if not self.connected:
            return None
        if 1 <= channel <= _IN_CH_COUNT:
            # Simulate temperature readings
            base_temp = 25.0
            temp_variation = random.uniform(-1.0, 1.0)
            return base_temp + temp_variation
        raise ValueError("Invalid input channel number.")

    def print_sensor_type(self, channel):
        sensor_type = self.get_sensor_type(channel)
        if sensor_type is not None:
            print(_TC_TYPES[sensor_type])

if IS_WINDOWS:
    SMtc = MockSMtc
else:
    class SMtc:
        def __init__(self, stack=0, i2c=1):
            if stack < 0 or stack > _STACK_LEVEL_MAX:
                raise ValueError('Invalid stack level!')
            self._hw_address_ = _CARD_BASE_ADDRESS + stack
            self._i2c_bus_no = i2c
            self._card_rev_major = 0
            self._card_rev_minor = 0
            self.connected = False
            # We don't connect automatically at init anymore.
            # The user will trigger connection via the UI.

        def connect(self):
            """Tries to connect to the board and read revision info."""
            try:
                bus = smbus2.SMBus(self._i2c_bus_no)
                self._card_rev_major = bus.read_byte_data(self._hw_address_, _REVISION_HW_MAJOR_MEM_ADD)
                self._card_rev_minor = bus.read_byte_data(self._hw_address_, _REVISION_HW_MINOR_MEM_ADD)
                bus.close()
                self.connected = True
                print("Successfully connected to SMTC board.")
                return True
            except Exception as e:
                self.connected = False
                print(f"Failed to connect to SMTC board: {e}")
                return False

        def disconnect(self):
            """Disconnects from the board."""
            self.connected = False
            print("Disconnected from SMTC board.")

        def get_board_info(self):
            """Returns a dictionary with board information."""
            return {
                "connected": self.connected,
                "hw_rev_major": self._card_rev_major,
                "hw_rev_minor": self._card_rev_minor,
            }

        def set_sensor_type(self, channel, cfg):
            if not self.connected:
                return
            if channel < 1 or channel > _IN_CH_COUNT:
                raise ValueError('Invalid input channel number must be [1..8]!')
            if cfg < _TC_TYPE_B or cfg > _TC_TYPE_T:
                raise ValueError('Invalid thermocouple type, must be [0..7]!')
            try:
                bus = smbus2.SMBus(self._i2c_bus_no)
                bus.write_byte_data(self._hw_address_, _TCP_TYPE1_ADD + channel - 1, cfg)
                bus.close()
            except Exception as e:
                print(f"Failed to set sensor type: {e}")
                self.connected = False

        def get_sensor_type(self, channel):
            if not self.connected:
                return None
            if channel < 1 or channel > _IN_CH_COUNT:
                raise ValueError('Invalid input channel number must be [1..8]!')
            try:
                bus = smbus2.SMBus(self._i2c_bus_no)
                val = bus.read_byte_data(self._hw_address_, _TCP_TYPE1_ADD + channel - 1)
                bus.close()
                return val
            except Exception as e:
                print(f"Failed to get sensor type: {e}")
                self.connected = False
                return None

        def get_temp(self, channel):
            if not self.connected:
                return None
            if channel < 1 or channel > _IN_CH_COUNT:
                raise ValueError('Invalid input channel number must be [1..8]!')
            try:
                bus = smbus2.SMBus(self._i2c_bus_no)
                buff = bus.read_i2c_block_data(self._hw_address_, _TCP_VAL1_ADD + (channel - 1) * _TEMP_SIZE_BYTES, 2)
                val = struct.unpack('h', bytearray(buff))
                bus.close()
                return val[0] / _TEMP_SCALE_FACTOR
            except Exception as e:
                print(f"Failed to read temperature for channel {channel}: {e}")
                self.connected = False
                return None

        def print_sensor_type(self, channel):
            sensor_type = self.get_sensor_type(channel)
            if sensor_type is not None:
                print(_TC_TYPES[sensor_type])