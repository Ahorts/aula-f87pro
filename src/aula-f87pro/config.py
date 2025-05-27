import json
import os
from typing import Any

class ConfigManager:
    def __init__(self, config_file_path: str):
        self.config_file_path = config_file_path
        self.config_data = {}
        self.load_config()
        
    
   
    def load_config(self):
        if os.path.exists(self.config_file_path):
            try:
                with open(self.config_file_path, 'r') as file:
                    self.config_data = json.load(file)

            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config: {e}")
                self.config_data = {} 
            
    def save_config(self):
        try:
            os.makedirs(os.path.dirname(self.config_file_path), exist_ok=True)
            with open(self.config_file_path, 'w') as file:
                json.dump(self.config_data, file, indent=2)

        except IOError as e:
            print(f"Error saving config: {e}")
            
            
    def get(self, key: str, default=None):
        return self.config_data.get(key, default)
    
    def set(self, key: str, value):
        self.config_data[key] = value
        self.save_config()