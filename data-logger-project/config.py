import json
import os
from typing import Dict, Any
from pathlib import Path

class Config:
    CONFIG_FILE = 'config.json'
    DEFAULT_CONFIG = {
        'database': {
            'type': 'sqlite',  # 'sqlite' or 'postgresql'
            'sqlite': {
                'path': 'datalogger.db'
            },
            'postgresql': {
                'host': 'localhost',
                'port': 5432,
                'database': 'datalogger',
                'username': '',
                'password': '',
                'ssl_mode': 'prefer'
            }
        },
        'storage': {
            'primary': 'local',  # 'local', 'sd', 'usb'
            'local_path': './data',
            'sd_path': '/media/sd',
            'usb_path': '/media/usb',
            'auto_detect': True
        },
        'logging': {
            'default_interval': 5,  # seconds
            'buffer_size': 100,  # records before flush
            'retention_days': 30  # data retention period
        },
        'system': {
            'auto_start': False,
            'web_port': 8080,
            'debug_mode': False
        },
        'telegram': {
            'bot_token': '8335298019:AAG6_ETjIY0juD_QPhQl900cxUKp7vKiF38',  # Get from @BotFather on Telegram
            'authorized_users': [],  # List of authorized Telegram user IDs
            'admin_users': [6921883539],  # List of admin user IDs (can authorize others)
            'group_chat_id': None,  # Optional: group chat ID for alerts
            'alerts_enabled': True,
            'alert_cooldown_minutes': 5
        },
        'email': {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'username': '',
            'password': '',  # Use app password for Gmail
            'from_email': '',
            'to_emails': [],
            'alerts_enabled': True
        },
        'channels': {
            '1': {'name': 'OVEN AIR', 'enabled': True},
            '2': {'name': 'FRYER SURF', 'enabled': True},
            '3': {'name': 'COAT MID', 'enabled': True},
            '4': {'name': 'COAT RIGHT', 'enabled': True},
            '5': {'name': 'COAT LEFT', 'enabled': True},
            '6': {'name': 'STEEL MID', 'enabled': True},
            '7': {'name': 'STEEL LEFT', 'enabled': True},
            '8': {'name': 'STEEL RIGHT', 'enabled': True}
        }
    }
    
    def __init__(self):
        self.config_path = Path(self.CONFIG_FILE)
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    user_config = json.load(f)
                    # Merge with defaults
                    return self._deep_merge(self.DEFAULT_CONFIG.copy(), user_config)
            except Exception as e:
                print(f"Error loading config: {e}, using defaults")
                return self.DEFAULT_CONFIG.copy()
        else:
            self.save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()
    
    def save_config(self, config: Dict[str, Any] = None):
        if config is None:
            config = self.config
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def get(self, key_path: str, default=None):
        keys = key_path.split('.')
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def set(self, key_path: str, value: Any):
        keys = key_path.split('.')
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value
        self.save_config(self.config)
    
    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                base[key] = self._deep_merge(base[key], value)
            else:
                base[key] = value
        return base

config = Config()