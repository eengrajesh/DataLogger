#!/usr/bin/env python3
"""
Test API Connect Endpoint
"""

from data_logger import connect, get_board_info

print("=" * 60)
print("  Testing Connect API")
print("=" * 60)

print("\n1. Calling connect()...")
result = connect()
print(f"   Result: {result}")

print("\n2. Getting board_info()...")
board_info = get_board_info()
print(f"   Board Info: {board_info}")

print("\n3. Checking 'connected' field...")
if 'connected' in board_info:
    print(f"   ✅ 'connected' field exists: {board_info['connected']}")
else:
    print(f"   ❌ 'connected' field MISSING!")
    print(f"   Available fields: {list(board_info.keys())}")

print("\n" + "=" * 60)
