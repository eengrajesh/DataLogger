#!/usr/bin/env python3
"""
GPIO Test Script for Enertherm DataLogger
Tests all GPIO buttons and LEDs functionality
Run this script to verify hardware connections
"""

import sys
import time
import logging
from data_logger_project.gpio_controller import GPIOController

def test_gpio_hardware():
    """Test GPIO hardware functionality"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 60)
    print("         ENERTHERM DATALOGGER GPIO TEST")
    print("=" * 60)
    print()
    
    # Initialize GPIO controller
    print("1. Initializing GPIO controller...")
    try:
        gpio_controller = GPIOController()
        gpio_controller.start()
        print("   ✓ GPIO controller initialized successfully")
    except Exception as e:
        print(f"   ✗ Failed to initialize GPIO controller: {e}")
        return False
    
    print()
    
    # Test LEDs
    print("2. Testing Status LEDs...")
    leds = ['SYSTEM', 'ERROR', 'NETWORK', 'LOGGING']
    
    try:
        for led in leds:
            print(f"   Testing {led} LED...")
            
            # Turn LED on
            gpio_controller.set_led(led, True)
            print(f"     → {led} LED ON (should be bright)")
            time.sleep(2)
            
            # Turn LED off
            gpio_controller.set_led(led, False)
            print(f"     → {led} LED OFF (should be dim/off)")
            time.sleep(1)
            
        print("   ✓ All LEDs tested successfully")
        
    except Exception as e:
        print(f"   ✗ LED test failed: {e}")
        
    print()
    
    # Test LED patterns
    print("3. Testing LED patterns...")
    try:
        print("   → All LEDs ON")
        for led in leds:
            gpio_controller.set_led(led, True)
        time.sleep(2)
        
        print("   → All LEDs OFF")
        for led in leds:
            gpio_controller.set_led(led, False)
        time.sleep(1)
        
        print("   → Sequential LED test")
        for led in leds:
            gpio_controller.set_led(led, True)
            time.sleep(0.5)
            gpio_controller.set_led(led, False)
            time.sleep(0.2)
            
        print("   ✓ LED patterns completed")
        
    except Exception as e:
        print(f"   ✗ LED pattern test failed: {e}")
        
    print()
    
    # Test button monitoring
    print("4. Testing Button Detection...")
    print("   Press each button to test (30 second timeout):")
    print("   - GREEN START button")
    print("   - RED SHUTDOWN button") 
    print("   - BLUE EXPORT button")
    print("   - YELLOW WIFI button")
    print("   Press Ctrl+C to skip button test")
    print()
    
    buttons_tested = set()
    start_time = time.time()
    
    try:
        while len(buttons_tested) < 4 and (time.time() - start_time) < 30:
            status = gpio_controller.get_status()
            
            for button, pressed in status['buttons'].items():
                if pressed and button not in buttons_tested:
                    print(f"   ✓ {button} button detected!")
                    buttons_tested.add(button)
                    
                    # Light up corresponding LED briefly
                    led_map = {
                        'START': 'SYSTEM',
                        'SHUTDOWN': 'ERROR', 
                        'EXPORT': 'NETWORK',
                        'WIFI': 'LOGGING'
                    }
                    if button in led_map:
                        gpio_controller.set_led(led_map[button], True)
                        time.sleep(0.5)
                        gpio_controller.set_led(led_map[button], False)
            
            time.sleep(0.1)
            
        if len(buttons_tested) == 4:
            print("   ✓ All buttons tested successfully!")
        else:
            print(f"   ⚠ Only {len(buttons_tested)}/4 buttons tested")
            
    except KeyboardInterrupt:
        print("   → Button test skipped by user")
        
    print()
    
    # Final status
    print("5. Final GPIO Status:")
    try:
        status = gpio_controller.get_status()
        print(f"   Platform: {status['platform']}")
        print(f"   Buttons: {status['buttons']}")
        print(f"   LEDs: {status['leds']}")
        
    except Exception as e:
        print(f"   ✗ Failed to get status: {e}")
        
    print()
    
    # Cleanup
    print("6. Cleaning up...")
    try:
        gpio_controller.cleanup()
        print("   ✓ GPIO cleanup completed")
    except Exception as e:
        print(f"   ✗ Cleanup failed: {e}")
        
    print()
    print("=" * 60)
    print("                    TEST COMPLETED")
    print("=" * 60)
    print()
    print("If all tests passed:")
    print("  1. All LEDs should have lit up during testing")
    print("  2. Button presses should have been detected")
    print("  3. No error messages should appear")
    print()
    print("If tests failed:")
    print("  1. Check wiring connections per GPIO_HARDWARE_GUIDE.txt")
    print("  2. Verify Pi5 GPIO pins are correctly connected")
    print("  3. Check that LEDs have correct polarity (+/-)")
    print("  4. Ensure 220Ω resistors are in series with LEDs")
    print()
    
    return True

def main():
    """Main test function"""
    try:
        test_gpio_hardware()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nTest failed with error: {e}")
    finally:
        print("Exiting GPIO test...")

if __name__ == "__main__":
    main()