import hid
import time
import json
import os
from typing import Optional
from config import ConfigManager

class AulaF87Pro:
    VENDOR_ID = 0x258a
    PRODUCT_ID = 0x010c
    
    def __init__(self):
        self.device = None
        self.device_path = None
        self.num_leds = 102
        self.config_manager = ConfigManager(os.path.expanduser("~/.aula_f87_config.json"))
    
    def find_working_interface(self) -> Optional[str]:
        print("Searching for working RGB interface...")
        
        devices = hid.enumerate(self.VENDOR_ID, self.PRODUCT_ID)
        
        for i, dev_info in enumerate(devices):
            try:
                print(f"Testing interface {i}")
                print(f"  Path: {dev_info['path']}")
                print(f"  Interface: {dev_info.get('interface_number', 'N/A')}")
                
                temp_device = hid.device()
                temp_device.open_path(dev_info['path'])
                
                # Test packet sent
                packet = [0x06, 0x08, 0x00, 0x00, 0x01, 0x00, 0x7a, 0x01]
                test_data = [255, 0, 0] * 10 + [0, 0, 0] * (self.num_leds - 10)
                packet.extend(test_data)
                packet.extend([0] * (520 - len(packet)))
                
                print(f"  Sending test packet ({len(packet)} bytes)...")
                temp_device.send_feature_report(packet)
                temp_device.close()
                
                print(f"  Interface {i} works! Saving configuration...")
                self.config_manager.set('device_path', dev_info['path'].decode('utf-8') if isinstance(dev_info['path'], bytes) else dev_info['path'])
                self.config_manager.set('vendor_id', self.VENDOR_ID)
                self.config_manager.set('product_id', self.PRODUCT_ID)
                self.config_manager.set('saved_at', time.time())
                
                return dev_info['path']
                
            except Exception as e:
                print(f"  Interface {i} failed: {e}")
        
        print("No working interface found!")
        return None

    def connect(self, device_path: str) -> bool:
        try:
            import hid
            self.device = hid.device()
            self.device.open_path(device_path)
            self.device_path = device_path
            
            return True
        
        except Exception as e:
            print(f"Failed to connect to device: {e}")
            return False
        
    def disconnect(self):
        if self.device:
            self.device.close()
            self.device = None
            
    
    def send_rgb(self, rgb_data: list) -> bool:
        if not self.device:
            print("Device not connected")
            return False
        
        try:
            packet = [0x06, 0x08, 0x00, 0x00, 0x01, 0x00, 0x7A, 0x01]
            packet.extend(rgb_data)
            packet.extend([0] * (520 - len(packet)))

            self.device.send_feature_report(packet)
            return True
        
        except Exception as e:
            print(f"Failed to send RGB data packet: {e}")
            return False
        
    
    def hex_to_rgb(self, hex_color: str) -> list:
        hex_color = hex_color.lstrip('#')
        return [int(hex_color[i:i + 2], 16) for i in (0, 2, 4)]

    def rgb_to_hex(self, rgb_color: list) -> str:
        return '#{:02x}{:02x}{:02x}'.format(*rgb_color)

