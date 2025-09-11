#!/usr/bin/env python3
"""
Quick Bot Token Test
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'data-logger-project'))

import asyncio
from telegram import Bot
from config import config

async def test_bot_token():
    # Get bot token from config
    bot_token = config.get('telegram.bot_token', '')
    admin_user = config.get('telegram.admin_users', [])
    
    print("=== QUICK BOT TEST ===")
    print(f"Bot token: {bot_token[:15]}...")
    print(f"Admin user: {admin_user}")
    
    if not bot_token:
        print("ERROR: No bot token configured!")
        return
    
    try:
        # Create bot instance
        bot = Bot(token=bot_token)
        
        # Test basic bot info
        me = await bot.get_me()
        print(f"SUCCESS: Bot connected!")
        print(f"Bot name: {me.first_name}")
        print(f"Bot username: @{me.username}")
        
        # Send a test message to admin user
        if admin_user:
            user_id = admin_user[0]
            await bot.send_message(
                chat_id=user_id,
                text="🎉 SUCCESS! Your DataLogger Telegram bot is working!\n\nYour bot is ready to use. Try sending /start to see the main menu."
            )
            print(f"SUCCESS: Test message sent to user {user_id}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_bot_token())
    if result:
        print("\n✓ Bot token is valid and working!")
        print("✓ Check your iPhone Telegram for test message!")
        print("\nNow you can:")
        print("1. Find your bot in Telegram")
        print("2. Send /start to begin")
        print("3. Try all the commands!")
    else:
        print("\n✗ Bot test failed - check your configuration")