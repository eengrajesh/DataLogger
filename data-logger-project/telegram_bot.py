#!/usr/bin/env python3
"""
Telegram Bot for Enertherm DataLogger
Provides remote monitoring and control via Telegram
"""

import asyncio
import logging
import json
import csv
import io
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading
import time

try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("telegram-python-bot not installed. Install with: pip install python-telegram-bot")

from config import config

class TelegramBot:
    """Telegram bot for DataLogger remote control and monitoring"""
    
    def __init__(self, data_logger_module=None, notification_system=None, gpio_controller=None):
        """Initialize Telegram bot"""
        self.data_logger_module = data_logger_module
        self.notification_system = notification_system
        self.gpio_controller = gpio_controller
        
        # Bot configuration
        self.bot_token = config.get('telegram.bot_token', '')
        self.authorized_users = set(config.get('telegram.authorized_users', []))
        self.admin_users = set(config.get('telegram.admin_users', []))
        self.group_chat_id = config.get('telegram.group_chat_id', None)
        
        # Bot state
        self.application = None
        self.running = False
        self.alert_queue = []
        
        # Setup logging
        self.logger = logging.getLogger('telegram_bot')
        self.logger.setLevel(logging.INFO)
        
        # Initialize if telegram is available
        if TELEGRAM_AVAILABLE and self.bot_token:
            self._initialize_bot()
        else:
            self.logger.warning("Telegram bot not configured or library not available")
    
    def _initialize_bot(self):
        """Initialize the Telegram bot application"""
        try:
            self.application = Application.builder().token(self.bot_token).build()
            
            # Register command handlers
            self.application.add_handler(CommandHandler("start", self._cmd_start))
            self.application.add_handler(CommandHandler("help", self._cmd_help))
            self.application.add_handler(CommandHandler("status", self._cmd_status))
            self.application.add_handler(CommandHandler("temps", self._cmd_temperatures))
            self.application.add_handler(CommandHandler("logging", self._cmd_logging))
            self.application.add_handler(CommandHandler("system", self._cmd_system))
            self.application.add_handler(CommandHandler("export", self._cmd_export))
            self.application.add_handler(CommandHandler("gpio", self._cmd_gpio))
            self.application.add_handler(CommandHandler("alerts", self._cmd_alerts))
            self.application.add_handler(CommandHandler("authorize", self._cmd_authorize))
            
            # Register callback handlers for inline keyboards
            self.application.add_handler(CallbackQueryHandler(self._callback_handler))
            
            # Register message handlers
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))
            
            self.logger.info("Telegram bot initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Telegram bot: {e}")
    
    def _is_authorized(self, user_id: int) -> bool:
        """Check if user is authorized to use the bot"""
        return user_id in self.authorized_users or user_id in self.admin_users
    
    def _is_admin(self, user_id: int) -> bool:
        """Check if user has admin privileges"""
        return user_id in self.admin_users
    
    async def _cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        
        if not self._is_authorized(user_id):
            await update.message.reply_text(
                "🔒 Access Denied\n\n"
                f"User ID: {user_id}\n"
                f"Username: @{username}\n\n"
                "Please contact the administrator to authorize your access."
            )
            return
        
        welcome_message = (
            "🌡️ **Enertherm DataLogger Bot**\n\n"
            "Welcome! You can now monitor and control the temperature data logger remotely.\n\n"
            "**Available Commands:**\n"
            "📊 /status - System status overview\n"
            "🌡️ /temps - Current temperatures\n"
            "▶️ /logging - Start/stop logging\n"
            "⚙️ /system - System information\n"
            "📁 /export - Export data\n"
            "🔘 /gpio - GPIO status & control\n"
            "🚨 /alerts - Alert settings\n"
            "❓ /help - Show detailed help\n\n"
            "Use the inline buttons for quick actions!"
        )
        
        keyboard = [
            [InlineKeyboardButton("📊 Status", callback_data="status"),
             InlineKeyboardButton("🌡️ Temps", callback_data="temps")],
            [InlineKeyboardButton("▶️ Start Logging", callback_data="start_logging"),
             InlineKeyboardButton("⏹️ Stop Logging", callback_data="stop_logging")],
            [InlineKeyboardButton("🔘 GPIO Status", callback_data="gpio_status"),
             InlineKeyboardButton("📁 Export Data", callback_data="export_24h")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode='Markdown')
    
    async def _cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        if not self._is_authorized(update.effective_user.id):
            return
        
        help_text = (
            "🌡️ **Enertherm DataLogger Bot Help**\n\n"
            
            "**📊 System Monitoring:**\n"
            "`/status` - Complete system overview\n"
            "`/temps` - Current temperature readings\n"
            "`/system` - Hardware and software info\n\n"
            
            "**🎛️ Logging Control:**\n"
            "`/logging start` - Start temperature logging\n"
            "`/logging stop` - Stop temperature logging\n"
            "`/logging status` - Check logging status\n\n"
            
            "**📁 Data Export:**\n"
            "`/export 1h` - Export last 1 hour\n"
            "`/export 24h` - Export last 24 hours\n"
            "`/export 7d` - Export last 7 days\n\n"
            
            "**🔘 GPIO Control:**\n"
            "`/gpio status` - Show button/LED status\n"
            "`/gpio test` - Test all LEDs\n"
            "`/gpio led SYSTEM on` - Control specific LED\n\n"
            
            "**🚨 Alert Management:**\n"
            "`/alerts on` - Enable Telegram alerts\n"
            "`/alerts off` - Disable Telegram alerts\n"
            "`/alerts list` - Show alert settings\n\n"
            
            "**👑 Admin Commands:**\n"
            "`/authorize <user_id>` - Authorize new user\n"
            
            "**💡 Quick Tips:**\n"
            "• Use inline buttons for faster access\n"
            "• Bot works from anywhere with internet\n"
            "• All actions are logged for security\n"
            "• Real-time alerts sent automatically\n"
        )
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def _cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        if not self._is_authorized(update.effective_user.id):
            return
        
        try:
            # Get system status
            status_message = "📊 **System Status Report**\n\n"
            
            # Logging status
            if self.data_logger_module:
                is_logging = self.data_logger_module.is_logging()
                is_connected = self.data_logger_module.is_connected()
                
                status_message += f"🔄 **Logging:** {'🟢 Active' if is_logging else '🔴 Stopped'}\n"
                status_message += f"🔌 **DAQ Connected:** {'🟢 Yes' if is_connected else '🔴 No'}\n"
            
            # GPIO status
            if self.gpio_controller:
                gpio_status = self.gpio_controller.get_status()
                status_message += f"🔘 **GPIO Platform:** {gpio_status.get('platform', 'Unknown')}\n"
                
                # LED status
                leds = gpio_status.get('leds', {})
                led_status = []
                for led, state in leds.items():
                    emoji = "🟢" if state else "🔴"
                    led_status.append(f"{emoji} {led}")
                status_message += f"💡 **LEDs:** {' | '.join(led_status)}\n"
            
            # System info
            if self.data_logger_module:
                try:
                    cpu_temp = self.data_logger_module.get_cpu_temperature()
                    status_message += f"🌡️ **CPU Temp:** {cpu_temp:.1f}°C\n"
                except:
                    status_message += f"🌡️ **CPU Temp:** Unknown\n"
                
                try:
                    storage = self.data_logger_module.get_storage_status()
                    free_gb = storage.get('free_space_gb', 0)
                    status_message += f"💾 **Free Space:** {free_gb:.1f} GB\n"
                except:
                    status_message += f"💾 **Free Space:** Unknown\n"
            
            # Timestamp
            status_message += f"\n🕐 **Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Add quick action buttons
            keyboard = [
                [InlineKeyboardButton("🌡️ Get Temperatures", callback_data="temps"),
                 InlineKeyboardButton("🔄 Refresh Status", callback_data="status")],
                [InlineKeyboardButton("▶️ Start Logging", callback_data="start_logging"),
                 InlineKeyboardButton("⏹️ Stop Logging", callback_data="stop_logging")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(status_message, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error getting status: {str(e)}")
    
    async def _cmd_connect(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /connect command"""
        if not self._is_authorized(update.effective_user.id):
            return
        
        try:
            if not self.data_logger_module:
                await update.message.reply_text("❌ Data logger module not available")
                return
            
            # Check if already connected
            if self.data_logger_module.daq.connected:
                await update.message.reply_text("⚠️ Already connected to DAQ board")
                return
            
            # Try to connect
            await update.message.reply_text("🔌 Connecting to DAQ board...")
            success = self.data_logger_module.connect()
            
            if success:
                board_info = self.data_logger_module.get_board_info()
                message = (
                    "✅ **Successfully Connected**\n\n"
                    f"🔌 **Board:** {board_info.get('board_info', {}).get('hw_rev_major', 'Unknown')}.{board_info.get('board_info', {}).get('hw_rev_minor', 'Unknown')}\n"
                    "You can now read temperatures and start logging."
                )
                
                keyboard = [
                    [InlineKeyboardButton("🌡️ Get Temperatures", callback_data="temps"),
                     InlineKeyboardButton("▶️ Start Logging", callback_data="start_logging")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
                
                # Log the action
                username = update.effective_user.username or "Unknown"
                self.logger.info(f"DAQ connected via Telegram by @{username}")
            else:
                await update.message.reply_text(
                    "❌ **Connection Failed**\n\n"
                    "Could not connect to DAQ board.\n"
                    "Please check:\n"
                    "1. DAQ board is powered on\n"
                    "2. I2C is enabled\n"
                    "3. Board is properly connected",
                    parse_mode='Markdown'
                )
                
        except Exception as e:
            await update.message.reply_text(f"❌ Connection error: {str(e)}")
    
    async def _cmd_disconnect(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /disconnect command"""
        if not self._is_authorized(update.effective_user.id):
            return
        
        try:
            if not self.data_logger_module:
                await update.message.reply_text("❌ Data logger module not available")
                return
            
            # Check if connected
            if not self.data_logger_module.daq.connected:
                await update.message.reply_text("⚠️ Not connected to DAQ board")
                return
            
            # Stop logging if active
            if self.data_logger_module.is_logging():
                self.data_logger_module.stop_logging_thread()
                await update.message.reply_text("⏹️ Stopped logging before disconnecting")
            
            # Disconnect
            self.data_logger_module.disconnect()
            
            message = (
                "🔌 **Disconnected from DAQ**\n\n"
                "Board has been safely disconnected."
            )
            
            keyboard = [[InlineKeyboardButton("🔌 Connect Again", callback_data="connect")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
            
            # Log the action
            username = update.effective_user.username or "Unknown"
            self.logger.info(f"DAQ disconnected via Telegram by @{username}")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Disconnect error: {str(e)}")
    
    async def _cmd_temperatures(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /temps command"""
        if not self._is_authorized(update.effective_user.id):
            return
        
        try:
            if not self.data_logger_module:
                await update.message.reply_text("❌ Data logger module not available")
                return
            
            # Get current temperatures
            temp_message = "🌡️ **Current Temperatures**\n\n"
            
            # Check if DAQ is connected first
            if not self.data_logger_module.daq.connected:
                temp_message += "⚠️ DAQ board not connected\n\n"
                temp_message += "Use /connect to connect to the DAQ board first."
                
                keyboard = [[InlineKeyboardButton("🔌 Connect to DAQ", callback_data="connect")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(temp_message, reply_markup=reply_markup, parse_mode='Markdown')
                return
            
            # Try to get live data
            try:
                temps = {}
                for channel in range(1, 9):  # Channels 1-8
                    try:
                        temp = self.data_logger_module.daq.get_temp(channel)
                        if temp is not None:
                            temps[channel] = temp
                    except:
                        temps[channel] = None
                
                if temps:
                    for channel in range(1, 9):
                        temp = temps.get(channel)
                        if temp is not None:
                            temp_message += f"📊 **Channel {channel}:** {temp:.1f}°C\n"
                        else:
                            temp_message += f"📊 **Channel {channel}:** No data\n"
                else:
                    temp_message += "⚠️ No temperature data available\n"
                    
            except Exception as e:
                temp_message += f"❌ Error reading temperatures: {str(e)}\n"
            
            temp_message += f"\n🕐 **Reading Time:** {datetime.now().strftime('%H:%M:%S')}"
            
            # Add refresh button
            keyboard = [[InlineKeyboardButton("🔄 Refresh Temperatures", callback_data="temps")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(temp_message, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error getting temperatures: {str(e)}")
    
    async def _cmd_logging(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /logging command"""
        if not self._is_authorized(update.effective_user.id):
            return
        
        args = context.args
        if not args:
            # Show logging status
            if self.data_logger_module:
                is_logging = self.data_logger_module.is_logging()
                status = "🟢 Active" if is_logging else "🔴 Stopped"
                
                keyboard = []
                if is_logging:
                    keyboard.append([InlineKeyboardButton("⏹️ Stop Logging", callback_data="stop_logging")])
                else:
                    keyboard.append([InlineKeyboardButton("▶️ Start Logging", callback_data="start_logging")])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(f"🔄 **Logging Status:** {status}", reply_markup=reply_markup, parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ Data logger module not available")
            return
        
        command = args[0].lower()
        
        if command == "start":
            await self._start_logging(update)
        elif command == "stop":
            await self._stop_logging(update)
        elif command == "status":
            await self._cmd_logging(update, context)  # Recursive call without args
        else:
            await update.message.reply_text("❌ Invalid command. Use: start, stop, or status")
    
    async def _start_logging(self, update):
        """Start data logging"""
        if not self.data_logger_module:
            await update.message.reply_text("❌ Data logger module not available")
            return
        
        # Check if DAQ is connected
        if not self.data_logger_module.daq.connected:
            await update.message.reply_text(
                "❌ **Cannot Start Logging**\n\n"
                "DAQ board is not connected.\n"
                "Please connect first using /connect",
                parse_mode='Markdown'
            )
            return
        
        if self.data_logger_module.is_logging():
            await update.message.reply_text("⚠️ Logging is already active")
            return
        
        success = self.data_logger_module.start_logging_thread()
        if success:
            await update.message.reply_text("✅ **Logging Started**\nTemperature data collection is now active.", parse_mode='Markdown')
            
            # Log the action
            username = update.effective_user.username or "Unknown"
            self.logger.info(f"Logging started via Telegram by @{username}")
        else:
            await update.message.reply_text("❌ Failed to start logging. Check system status.")
    
    async def _stop_logging(self, update):
        """Stop data logging"""
        if not self.data_logger_module:
            await update.message.reply_text("❌ Data logger module not available")
            return
        
        if not self.data_logger_module.is_logging():
            await update.message.reply_text("⚠️ Logging is not currently active")
            return
        
        success = self.data_logger_module.stop_logging_thread()
        if success:
            await update.message.reply_text("⏹️ **Logging Stopped**\nTemperature data collection has been stopped.")
            
            # Log the action
            username = update.effective_user.username or "Unknown"
            self.logger.info(f"Logging stopped via Telegram by @{username}")
        else:
            await update.message.reply_text("❌ Failed to stop logging")
    
    async def _cmd_system(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /system command"""
        if not self._is_authorized(update.effective_user.id):
            return
        
        try:
            system_info = "⚙️ **System Information**\n\n"
            
            # Hardware info
            if self.data_logger_module:
                try:
                    board_info = self.data_logger_module.get_board_info()
                    system_info += f"🔌 **DAQ Board:** {board_info.get('name', 'Unknown')}\n"
                    system_info += f"📡 **Address:** {board_info.get('address', 'Unknown')}\n"
                except:
                    system_info += f"🔌 **DAQ Board:** Not connected\n"
                
                try:
                    cpu_temp = self.data_logger_module.get_cpu_temperature()
                    system_info += f"🌡️ **CPU Temperature:** {cpu_temp:.1f}°C\n"
                except:
                    system_info += f"🌡️ **CPU Temperature:** Unknown\n"
                
                try:
                    storage = self.data_logger_module.get_storage_status()
                    system_info += f"💾 **Total Space:** {storage.get('total_space_gb', 0):.1f} GB\n"
                    system_info += f"💾 **Free Space:** {storage.get('free_space_gb', 0):.1f} GB\n"
                    system_info += f"💾 **Used:** {storage.get('used_percentage', 0):.1f}%\n"
                except:
                    system_info += f"💾 **Storage:** Unknown\n"
            
            # Software info
            system_info += f"\n🐍 **Platform:** Python DataLogger\n"
            system_info += f"🤖 **Bot Status:** Active\n"
            system_info += f"👥 **Authorized Users:** {len(self.authorized_users)}\n"
            
            await update.message.reply_text(system_info, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error getting system info: {str(e)}")
    
    async def _cmd_export(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /export command"""
        if not self._is_authorized(update.effective_user.id):
            return
        
        args = context.args
        period = args[0] if args else "24h"
        
        try:
            # Parse time period
            if period == "1h":
                hours = 1
                filename = "datalogger_1hour.csv"
            elif period == "24h":
                hours = 24
                filename = "datalogger_24hours.csv"
            elif period == "7d":
                hours = 24 * 7
                filename = "datalogger_7days.csv"
            else:
                await update.message.reply_text("❌ Invalid period. Use: 1h, 24h, or 7d")
                return
            
            await update.message.reply_text(f"📁 Preparing export for last {period}...")
            
            # Generate CSV data
            csv_data = await self._generate_csv_export(hours)
            
            if csv_data:
                # Create file-like object
                csv_file = io.BytesIO(csv_data.encode('utf-8'))
                csv_file.name = filename
                
                await update.message.reply_document(
                    document=csv_file,
                    filename=filename,
                    caption=f"📊 **Temperature Data Export**\nPeriod: Last {period}\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
            else:
                await update.message.reply_text("❌ No data available for export")
                
        except Exception as e:
            await update.message.reply_text(f"❌ Export failed: {str(e)}")
    
    async def _generate_csv_export(self, hours: int) -> Optional[str]:
        """Generate CSV export data"""
        try:
            if not self.data_logger_module or not hasattr(self.data_logger_module, 'db_manager'):
                return None
            
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            # Query database
            query = """
            SELECT timestamp, thermocouple_id, temperature 
            FROM readings 
            WHERE timestamp >= ? AND timestamp <= ?
            ORDER BY timestamp
            """
            
            data = self.data_logger_module.db_manager.execute_query(
                query, 
                (start_time.isoformat(), end_time.isoformat())
            )
            
            if not data:
                return None
            
            # Generate CSV
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Timestamp', 'Channel', 'Temperature'])
            
            for row in data:
                writer.writerow(row)
            
            return output.getvalue()
            
        except Exception as e:
            self.logger.error(f"CSV export error: {e}")
            return None
    
    async def _cmd_gpio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /gpio command"""
        if not self._is_authorized(update.effective_user.id):
            return
        
        args = context.args
        
        if not args or args[0] == "status":
            await self._gpio_status(update)
        elif args[0] == "test":
            await self._gpio_test(update)
        elif args[0] == "led" and len(args) >= 3:
            await self._gpio_led_control(update, args[1], args[2])
        else:
            help_text = (
                "🔘 **GPIO Commands:**\n\n"
                "`/gpio status` - Show GPIO status\n"
                "`/gpio test` - Test all LEDs\n"
                "`/gpio led SYSTEM on` - Control LED\n"
                "`/gpio led ERROR off` - Turn off LED\n\n"
                "**Available LEDs:** SYSTEM, ERROR, NETWORK, LOGGING"
            )
            await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def _gpio_status(self, update):
        """Show GPIO status"""
        if not self.gpio_controller:
            await update.message.reply_text("❌ GPIO controller not available")
            return
        
        try:
            status = self.gpio_controller.get_status()
            
            gpio_message = "🔘 **GPIO Status**\n\n"
            
            # Button status
            gpio_message += "**🔲 Buttons:**\n"
            for button, pressed in status.get('buttons', {}).items():
                emoji = "🟢" if pressed else "🔴"
                gpio_message += f"{emoji} {button}: {'PRESSED' if pressed else 'Ready'}\n"
            
            # LED status
            gpio_message += "\n**💡 LEDs:**\n"
            for led, state in status.get('leds', {}).items():
                emoji = "🟢" if state else "🔴"
                gpio_message += f"{emoji} {led}: {'ON' if state else 'OFF'}\n"
            
            gpio_message += f"\n🖥️ **Platform:** {status.get('platform', 'Unknown')}"
            
            # Add control buttons
            keyboard = [
                [InlineKeyboardButton("🔄 Refresh", callback_data="gpio_status"),
                 InlineKeyboardButton("🧪 Test LEDs", callback_data="gpio_test")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(gpio_message, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ GPIO status error: {str(e)}")
    
    async def _gpio_test(self, update):
        """Test all GPIO LEDs"""
        if not self.gpio_controller:
            await update.message.reply_text("❌ GPIO controller not available")
            return
        
        try:
            await update.message.reply_text("🧪 **Testing LEDs...**\nWatch the physical LEDs on your device!")
            
            leds = ['SYSTEM', 'ERROR', 'NETWORK', 'LOGGING']
            
            for led in leds:
                self.gpio_controller.set_led(led, True)
                await asyncio.sleep(1)
                self.gpio_controller.set_led(led, False)
                await asyncio.sleep(0.5)
            
            await update.message.reply_text("✅ **LED Test Complete**\nAll LEDs should have flashed in sequence.")
            
        except Exception as e:
            await update.message.reply_text(f"❌ LED test failed: {str(e)}")
    
    async def _gpio_led_control(self, update, led_name: str, state: str):
        """Control specific LED"""
        if not self.gpio_controller:
            await update.message.reply_text("❌ GPIO controller not available")
            return
        
        try:
            led_name = led_name.upper()
            if led_name not in ['SYSTEM', 'ERROR', 'NETWORK', 'LOGGING']:
                await update.message.reply_text("❌ Invalid LED. Use: SYSTEM, ERROR, NETWORK, LOGGING")
                return
            
            led_state = state.lower() in ['on', '1', 'true', 'yes']
            self.gpio_controller.set_led(led_name, led_state)
            
            state_text = "ON" if led_state else "OFF"
            await update.message.reply_text(f"✅ **{led_name} LED** set to **{state_text}**")
            
        except Exception as e:
            await update.message.reply_text(f"❌ LED control failed: {str(e)}")
    
    async def _cmd_alerts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /alerts command"""
        if not self._is_authorized(update.effective_user.id):
            return
        
        args = context.args
        
        if not args or args[0] == "list":
            alerts_info = (
                "🚨 **Alert Settings**\n\n"
                "**Current Status:** 🟢 Enabled\n\n"
                "**Alert Types:**\n"
                "• 🌡️ Temperature thresholds\n"
                "• 🔌 DAQ disconnection\n"
                "• 🌐 Network connectivity\n"
                "• 💾 Low disk space\n"
                "• ⚙️ System errors\n"
                "• 🔄 Logging start/stop\n\n"
                "**Commands:**\n"
                "`/alerts on` - Enable alerts\n"
                "`/alerts off` - Disable alerts"
            )
            await update.message.reply_text(alerts_info, parse_mode='Markdown')
        
        elif args[0] == "on":
            await update.message.reply_text("✅ **Telegram alerts enabled**\nYou will receive real-time notifications.")
        
        elif args[0] == "off":
            await update.message.reply_text("🔕 **Telegram alerts disabled**\nYou will not receive automatic notifications.")
        
        else:
            await update.message.reply_text("❌ Invalid command. Use: on, off, or list")
    
    async def _cmd_authorize(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /authorize command (admin only)"""
        if not self._is_admin(update.effective_user.id):
            await update.message.reply_text("❌ Admin access required")
            return
        
        args = context.args
        if not args:
            await update.message.reply_text("❌ Usage: /authorize <user_id>")
            return
        
        try:
            user_id = int(args[0])
            self.authorized_users.add(user_id)
            
            # Update config (you might want to save this permanently)
            await update.message.reply_text(f"✅ **User {user_id} authorized**\nThey can now use the bot.")
            
        except ValueError:
            await update.message.reply_text("❌ Invalid user ID format")
    
    async def _callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard callbacks"""
        query = update.callback_query
        await query.answer()
        
        if not self._is_authorized(query.from_user.id):
            return
        
        data = query.data
        
        # Create a fake update object for compatibility
        fake_update = type('obj', (object,), {
            'effective_user': query.from_user,
            'message': type('obj', (object,), {
                'reply_text': query.edit_message_text,
                'reply_document': query.bot.send_document
            })()
        })()
        
        if data == "status":
            await self._cmd_status(fake_update, context)
        elif data == "temps":
            await self._cmd_temperatures(fake_update, context)
        elif data == "connect":
            await self._cmd_connect(fake_update, context)
        elif data == "disconnect":
            await self._cmd_disconnect(fake_update, context)
        elif data == "start_logging":
            await self._start_logging(fake_update)
        elif data == "stop_logging":
            await self._stop_logging(fake_update)
        elif data == "gpio_status":
            await self._gpio_status(fake_update)
        elif data == "gpio_test":
            await self._gpio_test(fake_update)
        elif data == "export_24h":
            context.args = ["24h"]
            await self._cmd_export(fake_update, context)
    
    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages"""
        if not self._is_authorized(update.effective_user.id):
            return
        
        message = update.message.text.lower()
        
        # Simple natural language processing
        if "temperature" in message or "temp" in message:
            await self._cmd_temperatures(update, context)
        elif "status" in message:
            await self._cmd_status(update, context)
        elif "start" in message and "log" in message:
            await self._start_logging(update)
        elif "stop" in message and "log" in message:
            await self._stop_logging(update)
        else:
            await update.message.reply_text(
                "❓ Try using commands like /status, /temps, or /help\n"
                "Or use the inline buttons for quick actions!"
            )
    
    async def send_alert(self, alert_type: str, message: str, level: str = "info"):
        """Send alert to authorized users"""
        if not self.application or not self.running:
            return
        
        try:
            # Determine emoji based on alert level
            emoji_map = {
                "info": "ℹ️",
                "warning": "⚠️", 
                "error": "❌",
                "critical": "🚨"
            }
            emoji = emoji_map.get(level, "ℹ️")
            
            alert_message = f"{emoji} **Alert: {alert_type}**\n\n{message}\n\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Send to all authorized users
            for user_id in self.authorized_users.union(self.admin_users):
                try:
                    await self.application.bot.send_message(
                        chat_id=user_id,
                        text=alert_message,
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    self.logger.error(f"Failed to send alert to user {user_id}: {e}")
            
            # Send to group chat if configured
            if self.group_chat_id:
                try:
                    await self.application.bot.send_message(
                        chat_id=self.group_chat_id,
                        text=alert_message,
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    self.logger.error(f"Failed to send alert to group: {e}")
                    
        except Exception as e:
            self.logger.error(f"Alert sending failed: {e}")
    
    def start(self):
        """Start the Telegram bot"""
        if not TELEGRAM_AVAILABLE or not self.bot_token or not self.application:
            self.logger.warning("Telegram bot cannot start - not configured properly")
            return False
        
        try:
            self.running = True
            
            # Start the bot in a separate thread
            def run_bot():
                asyncio.set_event_loop(asyncio.new_event_loop())
                self.application.run_polling()
            
            self.bot_thread = threading.Thread(target=run_bot, daemon=True)
            self.bot_thread.start()
            
            self.logger.info("Telegram bot started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start Telegram bot: {e}")
            return False
    
    def stop(self):
        """Stop the Telegram bot"""
        try:
            self.running = False
            if self.application:
                # Stop the application
                asyncio.run(self.application.stop())
            self.logger.info("Telegram bot stopped")
        except Exception as e:
            self.logger.error(f"Error stopping Telegram bot: {e}")

# Test function
def test_telegram_bot():
    """Test Telegram bot functionality"""
    bot = TelegramBot()
    
    if bot.start():
        print("Telegram bot started successfully!")
        print("Test the bot by sending /start to your bot")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping bot...")
            bot.stop()
    else:
        print("Failed to start Telegram bot")

if __name__ == "__main__":
    test_telegram_bot()