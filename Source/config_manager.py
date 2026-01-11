import json
import os

CONFIG_FILE = "settings.json"

class ConfigManager:
    @staticmethod
    def load_config():
        default_config = {
            "h": "0", "m": "0", "s": "0", "ms": "100",
            "btn": "Left", "type": "Single",
            "pos_mode": "Current", "x": "0", "y": "0",
            "hotkey_char": "s",
            "random_enabled": False, "random_amt": "0",
            "repeat_mode": "Infinite", "repeat_count": "1",
            "on_top": False
        }
        
        if not os.path.exists(CONFIG_FILE):
            return default_config
            
        try:
            with open(CONFIG_FILE, "r") as f:
                loaded = json.load(f)
                # Merge with default to ensure all keys exist
                config = default_config.copy()
                config.update(loaded)
                return config
        except:
            return default_config

    @staticmethod
    def save_config(config_dict):
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(config_dict, f, indent=4)
        except:
            pass
