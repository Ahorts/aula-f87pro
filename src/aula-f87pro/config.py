import json
import os

class ConfigManager:
    def __init__(self, config_file_path: str):
        self.config_file_path = config_file_path
        self.config_data = {}
        self.load_config()
        
    
    def load_config(self):
        if os.path.exists(self.config_file_path):
            with open(self.config_file_path, 'r') as file:
                self.config_data = json.load(file)
            
    def save_config(self):
        with open(self.config_file_path, 'w') as file:
            json.dump(self.config_data, file)
            
    def get(self, key: str, default=None):
        return self.config_data.get(key, default)
    
    def set(self, key: str, value):
        self.config_data[key] = value
        self.save_config()