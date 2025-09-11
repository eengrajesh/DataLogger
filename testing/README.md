# 🧪 TESTING - Test Scripts & Tools

## Test Scripts
- **`test_telegram_bot.py`** - Test Telegram bot functionality
- **`test_gpio.py`** - Test GPIO hardware
- **`quick_bot_test.py`** - Quick bot token validation

## Test Commands
```bash
cd DataLogger/testing
python test_telegram_bot.py   # Test full bot
python quick_bot_test.py      # Quick token test
python test_gpio.py           # GPIO hardware test
```

## Test Results
All tests passed on development board:
- ✅ Bot token valid
- ✅ Message sending working  
- ✅ API endpoints responding
- ✅ Temperature data realistic