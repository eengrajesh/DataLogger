#!/usr/bin/env python3
"""
Telegram Bot Test Script for Enertherm DataLogger
Test the Telegram bot functionality independently
"""

import sys
import time
import logging
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'data-logger-project'))

from telegram_bot import TelegramBot
from config import config

def test_telegram_bot():
    """Test Telegram bot functionality"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 60)
    print("         ENERTHERM DATALOGGER TELEGRAM BOT TEST")
    print("=" * 60)
    print()
    
    # Check configuration
    print("1. Checking Telegram Bot Configuration...")
    
    bot_token = config.get('telegram.bot_token', '')
    admin_users = config.get('telegram.admin_users', [])
    authorized_users = config.get('telegram.authorized_users', [])
    
    if not bot_token:
        print("   ❌ Bot token not configured!")
        print("   Please add your bot token to config.py:")
        print("   1. Get token from @BotFather on Telegram")
        print("   2. Edit config.py and add it to telegram.bot_token")
        return False
    
    print(f"   ✓ Bot token configured: {bot_token[:10]}...")
    
    if not admin_users:
        print("   ⚠️  No admin users configured")
        print("   Add your Telegram user ID to telegram.admin_users in config.py")
    else:
        print(f"   ✓ Admin users: {admin_users}")
    
    if authorized_users:
        print(f"   ✓ Authorized users: {authorized_users}")
    else:
        print("   ℹ️  No additional authorized users (only admins can use bot)")
    
    print()
    
    # Initialize bot
    print("2. Initializing Telegram Bot...")
    try:
        bot = TelegramBot()
        print("   ✓ Telegram bot initialized successfully")
    except Exception as e:
        print(f"   ❌ Failed to initialize bot: {e}")
        return False
    
    print()
    
    # Test bot start
    print("3. Starting Telegram Bot...")
    try:
        if bot.start():
            print("   ✓ Telegram bot started successfully!")
            print("   ✓ Bot is now listening for commands")
        else:
            print("   ❌ Failed to start Telegram bot")
            return False
    except Exception as e:
        print(f"   ❌ Bot start failed: {e}")
        return False
    
    print()
    
    # Instructions for testing
    print("4. Testing Instructions:")
    print("   📱 Open Telegram and find your bot")
    print("   🔍 Search for your bot username")
    print("   💬 Send /start to begin")
    print("   📊 Try commands like /status, /help")
    print("   🔘 Test inline buttons")
    print()
    
    print("5. Available Test Commands:")
    print("   /start       - Welcome message and main menu")
    print("   /help        - Detailed help information")  
    print("   /status      - System status (simulated)")
    print("   /temps       - Temperature readings (simulated)")
    print("   /logging     - Logging control")
    print("   /system      - System information")
    print("   /gpio        - GPIO status and control")
    print("   /alerts      - Alert configuration")
    print()
    
    print("6. Authorization Testing:")
    if admin_users:
        print(f"   👑 Admin users {admin_users} can use all commands")
        print("   🔐 Other users will see 'Access Denied'")
        print("   ➕ Use /authorize <user_id> to add new users")
    else:
        print("   ⚠️  Configure admin_users in config.py first")
    
    print()
    
    # Keep bot running
    print("7. Bot Status: RUNNING")
    print("   Press Ctrl+C to stop the test")
    print("=" * 60)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n8. Stopping Telegram Bot...")
        try:
            bot.stop()
            print("   ✓ Bot stopped successfully")
        except Exception as e:
            print(f"   ⚠️  Stop error: {e}")
        
        print("\n=" * 60)
        print("                 TEST COMPLETED")
        print("=" * 60)
        
        if bot_token and admin_users:
            print("\n✅ Bot test successful!")
            print("🚀 Your Telegram bot is ready for integration")
            print("\nNext steps:")
            print("1. Test all commands with your Telegram app")
            print("2. Add more authorized users if needed")
            print("3. Configure group chat for team alerts")
            print("4. Integrate bot with main DataLogger application")
        else:
            print("\n⚠️  Configuration incomplete")
            print("📝 Complete the configuration in config.py")
            print("🔑 Add bot token and admin user IDs")
        
        return True

def show_configuration_help():
    """Show configuration help"""
    print("\n🔧 TELEGRAM BOT CONFIGURATION HELP")
    print("=" * 50)
    print()
    print("1. Create your bot:")
    print("   • Message @BotFather on Telegram")
    print("   • Send /newbot")
    print("   • Choose name: 'Enertherm DataLogger Bot'")
    print("   • Choose username: 'your_datalogger_bot'")
    print("   • Save the bot token")
    print()
    print("2. Get your user ID:")
    print("   • Message @userinfobot on Telegram")
    print("   • It will reply with your user ID")
    print()
    print("3. Update config.py:")
    print("   telegram: {")
    print("     'bot_token': 'YOUR_BOT_TOKEN_HERE',")
    print("     'admin_users': [YOUR_USER_ID_HERE],")
    print("     'authorized_users': [],")
    print("   }")
    print()
    print("4. Run this test again")
    print()

def main():
    """Main test function"""
    try:
        # Check if basic config exists
        bot_token = config.get('telegram.bot_token', '')
        if not bot_token:
            print("⚠️  Telegram bot not configured")
            show_configuration_help()
            return
        
        test_telegram_bot()
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        print("\nTroubleshooting:")
        print("1. Check internet connection")
        print("2. Verify bot token is correct")
        print("3. Ensure python-telegram-bot is installed:")
        print("   pip install python-telegram-bot")

if __name__ == "__main__":
    main()