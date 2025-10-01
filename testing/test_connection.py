#!/usr/bin/env python3
"""
Test script to verify connection status handling on Pi5
"""

import sm_tc
import time

def test_connection():
    print("Testing SMTC board connection...")
    print("=" * 50)
    
    # Initialize DAQ
    daq = sm_tc.SMtc(0, 1)
    
    # Test 1: Check initial state (should be disconnected)
    print("\n1. Initial state check:")
    print(f"   Connected: {daq.connected}")
    print(f"   Board info: {daq.get_board_info()}")
    
    # Test 2: Try to read temperature when not connected
    print("\n2. Reading temperature when not connected:")
    for channel in range(1, 4):  # Test first 3 channels
        temp = daq.get_temp(channel)
        print(f"   Channel {channel}: {temp}")
        if temp is not None:
            print("   WARNING: Got temperature when not connected!")
    
    # Test 3: Connect to board
    print("\n3. Connecting to board:")
    result = daq.connect()
    print(f"   Connection result: {result}")
    print(f"   Connected: {daq.connected}")
    print(f"   Board info: {daq.get_board_info()}")
    
    # Test 4: Read temperatures when connected
    if daq.connected:
        print("\n4. Reading temperatures when connected:")
        for channel in range(1, 4):
            temp = daq.get_temp(channel)
            print(f"   Channel {channel}: {temp}°C")
    
    # Test 5: Disconnect
    print("\n5. Disconnecting from board:")
    daq.disconnect()
    print(f"   Connected: {daq.connected}")
    print(f"   Board info: {daq.get_board_info()}")
    
    # Test 6: Try to read after disconnect
    print("\n6. Reading temperature after disconnect:")
    temp = daq.get_temp(1)
    print(f"   Channel 1: {temp}")
    if temp is not None:
        print("   WARNING: Got temperature after disconnect!")
    
    print("\n" + "=" * 50)
    print("Test complete!")

if __name__ == '__main__':
    test_connection()