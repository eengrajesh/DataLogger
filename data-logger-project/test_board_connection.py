#!/usr/bin/env python3
"""
SMTC Board Connection Diagnostic Tool
Run this to diagnose connection issues
"""

import os
import sys
import platform

print("=" * 70)
print("  SMTC BOARD CONNECTION DIAGNOSTIC")
print("=" * 70)

# Test 1: Platform check
print("\n[1] Platform Check")
print(f"    OS: {platform.system()}")
print(f"    Platform: {platform.platform()}")
print(f"    Python: {sys.version}")

# Test 2: I2C device check
print("\n[2] I2C Device Check")
i2c_devices = [f for f in os.listdir('/dev') if f.startswith('i2c-')] if os.path.exists('/dev') else []
if i2c_devices:
    print(f"    ✅ Found I2C devices: {', '.join(i2c_devices)}")
    for dev in i2c_devices:
        dev_path = f'/dev/{dev}'
        if os.access(dev_path, os.R_OK | os.W_OK):
            print(f"    ✅ {dev_path} - readable/writable")
        else:
            print(f"    ❌ {dev_path} - permission denied")
else:
    print("    ❌ No I2C devices found!")
    print("    → Run: sudo raspi-config → Interface Options → Enable I2C")

# Test 3: Required packages
print("\n[3] Python Package Check")
try:
    import smbus2
    print(f"    ✅ smbus2 installed (version: {smbus2.__version__ if hasattr(smbus2, '__version__') else 'unknown'})")
except ImportError:
    print("    ❌ smbus2 NOT installed")
    print("    → Run: pip install smbus2")

# Test 4: Module import
print("\n[4] Module Import Check")
try:
    from sm_tc import SMtc
    print("    ✅ sm_tc module imported successfully")
except ImportError as e:
    print(f"    ❌ Failed to import sm_tc: {e}")
    sys.exit(1)

# Test 5: I2C scan (requires sudo)
print("\n[5] I2C Bus Scan")
print("    Attempting to scan I2C bus for devices...")
try:
    import subprocess
    result = subprocess.run(['i2cdetect', '-y', '1'],
                          capture_output=True,
                          text=True,
                          timeout=5)
    if result.returncode == 0:
        print("    I2C Bus 1 scan result:")
        for line in result.stdout.split('\n'):
            if line.strip():
                print(f"    {line}")

        # Check for address 0x16
        if '16' in result.stdout:
            print("\n    ✅ Device found at address 0x16 (SMTC board)")
        else:
            print("\n    ⚠️ No device at address 0x16")
            print("    → Check if HAT is properly seated on GPIO pins")
    else:
        print(f"    ⚠️ Scan failed: {result.stderr}")
except FileNotFoundError:
    print("    ⚠️ i2cdetect not found")
    print("    → Install: sudo apt install i2c-tools")
except Exception as e:
    print(f"    ⚠️ Scan error: {e}")

# Test 6: Create DAQ connection
print("\n[6] DAQ Connection Test")
try:
    print("    Creating SMtc instance...")
    daq = SMtc(stack=0, i2c=1)
    print(f"    DAQ object created")
    print(f"    Type: {type(daq).__name__}")

    # Check if it's mock or real
    is_mock = type(daq).__name__ == 'MockSMtc'
    if is_mock:
        print("    ⚠️ Using MOCK hardware (not real board)")
        print("    → This is normal on Windows/Mac, but NOT on Pi5!")

    print(f"    Connected status: {daq.connected}")

    if not daq.connected:
        print("\n    Attempting to connect...")
        try:
            result = daq.connect()
            print(f"    Connect result: {result}")
            print(f"    Connected status: {daq.connected}")
        except Exception as e:
            print(f"    ❌ Connect failed: {e}")
            import traceback
            traceback.print_exc()

    if daq.connected:
        print("\n    ✅ BOARD CONNECTED SUCCESSFULLY!")

        # Test 7: Read temperature
        print("\n[7] Temperature Read Test")
        try:
            for ch in range(1, 4):  # Test first 3 channels
                temp = daq.get_temp(ch)
                print(f"    Channel {ch}: {temp:.1f}°C")
        except Exception as e:
            print(f"    ⚠️ Read error: {e}")
    else:
        print("\n    ❌ BOARD NOT CONNECTED")
        print("\n    Troubleshooting steps:")
        print("    1. Check I2C is enabled: sudo raspi-config")
        print("    2. Check HAT is properly seated on GPIO pins")
        print("    3. Check permissions: sudo usermod -a -G i2c $USER")
        print("    4. Reboot: sudo reboot")
        print("    5. Run i2c scan: sudo i2cdetect -y 1")

except Exception as e:
    print(f"    ❌ DAQ creation failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("  DIAGNOSTIC COMPLETE")
print("=" * 70)
