# 🤖 Telegram Bot Setup Guide for Enertherm DataLogger

This guide will help you set up and configure the Telegram bot for remote monitoring and control of your DataLogger system.

## 📱 What the Telegram Bot Can Do

### **Remote Monitoring**
- 📊 Real-time system status
- 🌡️ Current temperature readings from all 8 channels
- 💾 Storage and CPU monitoring
- 🔘 GPIO button and LED status
- 📈 Historical data requests

### **Remote Control**
- ▶️ Start/stop temperature logging
- 🔘 Control GPIO LEDs remotely
- 📁 Export and download data files
- 🧪 Test hardware components
- ⚙️ System information queries

### **Real-Time Alerts**
- 🚨 Critical temperature alerts
- 🔌 DAQ hardware disconnection
- 🌐 Network connectivity issues
- 💾 Low disk space warnings
- ⚙️ System error notifications

---

## 🚀 Step 1: Create Your Telegram Bot

### **1.1 Contact BotFather**
1. Open Telegram and search for `@BotFather`
2. Start a conversation with `/start`
3. Create a new bot with `/newbot`
4. Choose a name: `Enertherm DataLogger Bot`
5. Choose a username: `enertherm_datalogger_bot` (must end with `_bot`)
6. **Save the bot token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### **1.2 Configure Bot Settings**
```
/setdescription - Set bot description
/setabouttext - Set about text
/setuserpic - Upload bot profile picture
/setcommands - Set command menu
```

**Recommended Commands for BotFather:**
```
start - Start the bot and show main menu
help - Show detailed help and commands
status - Get system status overview
temps - Get current temperature readings
logging - Start/stop temperature logging
system - Show system information
export - Export temperature data
gpio - GPIO status and control
alerts - Configure alert settings
```

---

## 🔧 Step 2: Install Required Dependencies

### **2.1 Install Python Telegram Bot Library**
```bash
pip install python-telegram-bot
```

### **2.2 Verify Installation**
```bash
python -c "import telegram; print('Telegram library installed successfully')"
```

---

## ⚙️ Step 3: Configure the Bot

### **3.1 Update Configuration File**
Edit your `data-logger-project/config.py` file and add:

```python
# Telegram Bot Configuration
TELEGRAM_CONFIG = {
    'bot_token': 'YOUR_BOT_TOKEN_HERE',  # From BotFather
    'authorized_users': [],  # Will be populated when users authorize
    'admin_users': [123456789],  # Your Telegram user ID (admin)
    'group_chat_id': None,  # Optional: group chat for team notifications
    'alerts_enabled': True,
    'alert_cooldown_minutes': 5  # Prevent spam
}
```

### **3.2 Find Your Telegram User ID**
1. Start your bot (temporarily)
2. Send `/start` to your bot
3. Check the logs for your user ID
4. Add your user ID to `admin_users` list

**Alternative method:**
1. Message `@userinfobot` on Telegram
2. It will reply with your user ID

### **3.3 Configure Authorization**
The bot uses a whitelist system for security:
- **Admin Users**: Can authorize new users and control system
- **Authorized Users**: Can monitor and control (no user management)
- **Unauthorized Users**: Cannot use the bot

---

## 🔌 Step 4: Integrate with DataLogger

### **4.1 Update app_enhanced.py**
Add Telegram bot initialization to your main application:

```python
# Add to imports
from telegram_bot import TelegramBot

# Add after GPIO controller initialization
try:
    # Initialize Telegram bot
    telegram_bot = TelegramBot(
        data_logger_module=data_logger,
        notification_system=notification_system,
        gpio_controller=gpio_controller
    )
    
    if telegram_bot.start():
        print("Telegram bot started - remote access enabled")
    else:
        print("Telegram bot failed to start - check configuration")
        
except Exception as e:
    print(f"Telegram bot initialization failed: {e}")
```

### **4.2 Update Cleanup Code**
Add bot cleanup in the finally block:

```python
# In the finally block
try:
    if 'telegram_bot' in locals():
        telegram_bot.stop()
        print("Telegram bot stopped")
except Exception as e:
    print(f"Telegram bot cleanup error: {e}")
```

---

## 🧪 Step 5: Test Your Bot

### **5.1 Start the DataLogger Application**
```bash
cd data-logger-project
python app_enhanced.py
```

### **5.2 Test Basic Commands**
1. Find your bot on Telegram: `@your_bot_username`
2. Send `/start` - you should see the welcome message
3. Try `/status` - should show system status
4. Try `/temps` - should show current temperatures
5. Test inline buttons for quick actions

### **5.3 Test Authorization**
1. Have someone else try to use your bot
2. They should see "Access Denied" message
3. Use `/authorize <their_user_id>` to grant access
4. They should now be able to use the bot

---

## 🚨 Step 6: Configure Alerts

### **6.1 Alert Types Available**
- **Temperature Alerts**: High/low temperature thresholds
- **System Alerts**: DAQ disconnection, logging start/stop
- **Network Alerts**: Internet connectivity issues
- **Hardware Alerts**: GPIO button presses, system shutdown
- **Storage Alerts**: Low disk space warnings

### **6.2 Alert Configuration**
Alerts are automatically sent to:
- All authorized users
- Admin users
- Group chat (if configured)

### **6.3 Test Alerts**
Force an alert by:
1. Disconnecting the DAQ hardware
2. Pressing physical GPIO buttons
3. Starting/stopping logging via web interface
4. Simulating high temperature readings

---

## 📱 Step 7: Bot Commands Reference

### **System Monitoring**
```
/status          - Complete system overview
/temps           - Current temperature readings
/system          - Hardware and software information
```

### **Logging Control**
```
/logging start   - Start temperature logging
/logging stop    - Stop temperature logging
/logging status  - Check current logging status
```

### **Data Export**
```
/export 1h       - Export last 1 hour of data
/export 24h      - Export last 24 hours of data
/export 7d       - Export last 7 days of data
```

### **GPIO Control**
```
/gpio status     - Show button and LED status
/gpio test       - Test all LEDs in sequence
/gpio led SYSTEM on   - Turn on specific LED
/gpio led ERROR off   - Turn off specific LED
```

### **Alert Management**
```
/alerts on       - Enable Telegram alerts
/alerts off      - Disable Telegram alerts
/alerts list     - Show current alert settings
```

### **Admin Commands**
```
/authorize 123456789  - Authorize new user by ID
```

---

## 🔒 Security Best Practices

### **7.1 Bot Token Security**
- **Never share your bot token publicly**
- Store it in environment variables or secure config
- Regenerate token if compromised via BotFather

### **7.2 User Authorization**
- Only authorize trusted users
- Regularly review authorized user list
- Remove access for users who no longer need it

### **7.3 Group Chat Security**
- Use private groups only
- Verify all group members
- Disable group invite links

---

## 🛠️ Troubleshooting

### **8.1 Bot Won't Start**
```
Error: Telegram bot cannot start - not configured properly
```
**Solution:**
- Check bot token is correct
- Verify internet connection
- Ensure python-telegram-bot is installed

### **8.2 Commands Don't Work**
```
Error: This bot can't be reached
```
**Solution:**
- Bot may be stopped
- Check bot token validity
- Verify bot is running in application

### **8.3 Authorization Issues**
```
Access Denied - User ID: 123456789
```
**Solution:**
- Add user ID to authorized_users list
- Use /authorize command as admin
- Check user ID is correct

### **8.4 Alerts Not Received**
- Check alerts are enabled with `/alerts on`
- Verify user is authorized
- Check notification system is running
- Test with manual alert trigger

---

## 📊 Advanced Features

### **9.1 Group Chat Integration**
1. Create a private Telegram group
2. Add your bot to the group
3. Get the group chat ID
4. Add it to configuration
5. All alerts will be sent to the group

### **9.2 Multiple Bot Instances**
For multiple DataLogger systems:
1. Create separate bots for each system
2. Use different bot tokens
3. Configure different authorized user lists
4. Use descriptive bot names

### **9.3 Custom Alert Thresholds**
Modify the notification system to integrate with Telegram:
```python
# In notification_system.py
if telegram_bot:
    await telegram_bot.send_alert(
        alert_type="Temperature Alert",
        message=f"Channel {channel}: {temperature}°C exceeds threshold",
        level="warning"
    )
```

---

## 🌟 Example Usage Scenarios

### **Scenario 1: Remote Monitoring**
- You're away from the lab
- Check system status: `/status`
- Get current readings: `/temps`
- Export data if needed: `/export 24h`

### **Scenario 2: Emergency Response**
- Receive critical temperature alert
- Check system status remotely
- Stop logging if necessary: `/logging stop`
- Contact on-site personnel

### **Scenario 3: Team Collaboration**
- Add team members to authorized users
- Create group chat for alerts
- Team receives real-time notifications
- Multiple people can control system

### **Scenario 4: Data Collection**
- Start logging remotely: `/logging start`
- Monitor progress with periodic `/status`
- Export data when complete: `/export 7d`
- Stop logging: `/logging stop`

---

## 📞 Support and Maintenance

### **10.1 Log Files**
Bot activities are logged in the application logs:
- User commands and responses
- Authorization attempts
- Alert sending status
- Error conditions

### **10.2 Regular Maintenance**
- Review authorized user list monthly
- Check bot token validity
- Update alert thresholds as needed
- Test all commands periodically

### **10.3 Updates and Upgrades**
- Keep python-telegram-bot library updated
- Monitor Telegram Bot API changes
- Test new features in development environment
- Backup configuration before updates

---

## ✅ Quick Setup Checklist

- [ ] Created bot with BotFather
- [ ] Saved bot token securely
- [ ] Installed python-telegram-bot library
- [ ] Updated config.py with bot settings
- [ ] Added your user ID to admin_users
- [ ] Integrated bot with app_enhanced.py
- [ ] Started DataLogger application
- [ ] Tested `/start` command
- [ ] Tested basic commands (`/status`, `/temps`)
- [ ] Configured authorized users
- [ ] Tested alert functionality
- [ ] Documented bot credentials securely

---

**🎉 Congratulations! Your Telegram bot is now ready for remote DataLogger monitoring and control!**

For additional support or feature requests, check the project documentation or contact the development team.