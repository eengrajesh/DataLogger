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