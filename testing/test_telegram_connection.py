#!/usr/bin/env python3
"""
Test script for Telegram bot connection features
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config import config
import data_logger

class TestTelegramBot:
    def __init__(self):
        self.bot_token = config.get('telegram.bot_token', '')
        self.authorized_users = set(config.get('telegram.authorized_users', []))
        
    async def test_connection_commands(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Test connection commands"""
        user_id = update.effective_user.id
        
        if user_id not in self.authorized_users:
            await update.message.reply_text("🔒 Not authorized")
            return
        
        test_message = (
            "🧪 **Testing Connection Features**\n\n"
            "This will test the new connection commands:\n\n"
        )
        
        # Test connection status
        is_connected = data_logger.daq.connected
        test_message += f"🔌 **Current Status:** {'Connected' if is_connected else 'Disconnected'}\n\n"
        
        # Show available commands
        test_message += "**Available Commands:**\n"
        test_message += "/connect - Connect to DAQ\n"
        test_message += "/disconnect - Disconnect from DAQ\n"
        test_message += "/status - Check connection status\n\n"
        
        # Create test buttons
        keyboard = [
            [InlineKeyboardButton("🔌 Connect", callback_data="test_connect"),
             InlineKeyboardButton("🔌 Disconnect", callback_data="test_disconnect")],
            [InlineKeyboardButton("📊 Check Status", callback_data="test_status"),
             InlineKeyboardButton("🌡️ Read Temps", callback_data="test_temps")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(test_message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "test_connect":
            if data_logger.daq.connected:
                await query.edit_message_text("⚠️ Already connected")
            else:
                success = data_logger.connect()
                if success:
                    await query.edit_message_text("✅ Successfully connected to DAQ!")
                else:
                    await query.edit_message_text("❌ Failed to connect")
        
        elif data == "test_disconnect":
            if not data_logger.daq.connected:
                await query.edit_message_text("⚠️ Not connected")
            else:
                data_logger.disconnect()
                await query.edit_message_text("🔌 Disconnected from DAQ")
        
        elif data == "test_status":
            status = "Connected 🔌" if data_logger.daq.connected else "Disconnected ❌"
            board_info = data_logger.get_board_info()
            message = (
                f"**Connection Status:** {status}\n"
                f"**Board Info:** {board_info}\n"
            )
            await query.edit_message_text(message, parse_mode='Markdown')
        
        elif data == "test_temps":
            if not data_logger.daq.connected:
                await query.edit_message_text("❌ Not connected. Connect first!")
            else:
                temps_msg = "**Temperature Readings:**\n\n"
                for ch in range(1, 4):  # Test first 3 channels
                    temp = data_logger.daq.get_temp(ch)
                    if temp is not None:
                        temps_msg += f"Channel {ch}: {temp:.1f}°C\n"
                    else:
                        temps_msg += f"Channel {ch}: No data\n"
                await query.edit_message_text(temps_msg, parse_mode='Markdown')

def main():
    """Main test function"""
    print("Starting Telegram Bot Connection Test...")
    
    bot_token = config.get('telegram.bot_token', '')
    if not bot_token:
        print("❌ No bot token configured in config.json")
        return
    
    test_bot = TestTelegramBot()
    
    # Create application
    application = Application.builder().token(bot_token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("test", test_bot.test_connection_commands))
    application.add_handler(CallbackQueryHandler(test_bot.handle_callback))
    
    print("✅ Bot started! Send /test to your bot to test connection features")
    print("Press Ctrl+C to stop...")
    
    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()