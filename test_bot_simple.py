#!/usr/bin/env python3
"""
Simple Telegram Bot Test for Windows
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'data-logger-project'))

import asyncio
from telegram_bot import TelegramBot
from config import config

def test_bot():
    print("=== TELEGRAM BOT TEST ===")
    print()
    
    # Check configuration
    bot_token = config.get('telegram.bot_token', '')
    admin_users = config.get('telegram.admin_users', [])
    
    if not bot_token:
        print("ERROR: Bot token not configured!")
        return False
    
    print(f"Bot token configured: {bot_token[:10]}...")
    print(f"Admin users: {admin_users}")
    print()
    
    # Test bot creation
    try:
        bot = TelegramBot()
        print("SUCCESS: Bot initialized")
    except Exception as e:
        print(f"ERROR: Bot initialization failed: {e}")
        return False
    
    # Test bot start
    try:
        if bot.start():
            print("SUCCESS: Bot started!")
            print("Now test on your iPhone:")
            print("1. Open Telegram")
            print("2. Find your bot")
            print("3. Send /start")
            print("4. Try the buttons!")
            print()
            print("Press Ctrl+C to stop...")
            
            # Keep running
            import time
            while True:
                time.sleep(1)
                
        else:
            print("ERROR: Bot failed to start")
            return False
            
    except KeyboardInterrupt:
        print("\nStopping bot...")
        bot.stop()
        print("Bot stopped successfully!")
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    test_bot()