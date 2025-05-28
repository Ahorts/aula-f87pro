import hid
import time
import json
import os
from typing import Optional
from .config import ConfigManager

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
            # Skip interface 0 - it's always the keyboard input interface
            if i == 0:
                print(f"Skipping interface {i} (keyboard input interface)")
                continue
                
            try:
                print(f"Testing interface {i}")
                print(f"  Path: {dev_info['path']}")
                print(f"  Interface: {dev_info.get('interface_number', 'N/A')}")
                print(f"  Usage Page: {hex(dev_info.get('usage_page', 0))}")
                print(f"  Usage: {hex(dev_info.get('usage', 0))}")
                
                temp_device = hid.device()
                temp_device.open_path(dev_info['path'])
                
                packet = [0x06, 0x08, 0x00, 0x00, 0x01, 0x00, 0x7a, 0x01]
                
                # Red data for first 10 LEDs, off for rest
                test_data = [255, 0, 0] * 10 + [0, 0, 0] * (self.num_leds - 10)
                packet.extend(test_data)
                packet.extend([0] * (520 - len(packet)))
                
                print(f"  Sending test packet ({len(packet)} bytes)...")
                
                try:
                    result = temp_device.send_feature_report(packet)
                    print(f"  Feature report result: {result}")
                    
                    time.sleep(0.5)
                    
                    response = input(f"  Did you see red lights on interface {i}? (y/n): ").lower().strip()
                    
                    if response == 'y' or response == 'yes':
                        print(f"Interface {i} works! Saving configuration...")
                        
                        clear_packet = packet.copy()
                        clear_packet[8:8 + self.num_leds * 3] = [0] * (self.num_leds * 3)
                        temp_device.send_feature_report(clear_packet)
                        
                        temp_device.close()
                        
                        self.config_manager.set('device_path', dev_info['path'].decode('utf-8') if isinstance(dev_info['path'], bytes) else dev_info['path'])
                        self.config_manager.set('vendor_id', self.VENDOR_ID)
                        self.config_manager.set('product_id', self.PRODUCT_ID)
                        self.config_manager.set('saved_at', time.time())
                        
                        return dev_info['path']
                    else:
                        print(f"  Interface {i} doesn't control RGB lighting")
                        
                except Exception as e:
                    print(f"  Feature report failed: {e}")
                
                temp_device.close()
                
            except Exception as e:
                print(f"  Interface {i} failed to open: {e}")
        
        print("No working interface found!")
        return None

    def verify_saved_interface(self, device_path: str) -> bool:
        try:
            print("Verifying saved interface...")
            
            if isinstance(device_path, str):
                device_path_bytes = device_path.encode('utf-8')
            else:
                device_path_bytes = device_path
            
            temp_device = hid.device()
            temp_device.open_path(device_path_bytes)
            
            # Test packet
            packet = [0x06, 0x08, 0x00, 0x00, 0x01, 0x00, 0x7a, 0x01]
            packet.extend([0] * (self.num_leds * 3))
            packet.extend([0] * (520 - len(packet)))
            
            temp_device.send_feature_report(packet)
            temp_device.close()
            
            print("Saved interface verified!")
            return True
            
        except Exception as e:
            print(f"Saved interface no longer works: {e}")
            return False

    def connect(self, force_find: bool = False) -> bool:
        
        if not force_find and not self.device_path:
            saved_path = self.config_manager.get('device_path')
            if saved_path and self.verify_saved_interface(saved_path):
                self.device_path = saved_path
        
        if force_find or not self.device_path:
            self.device_path = self.find_working_interface()
            if not self.device_path:
                return False
        
        try:
            self.device = hid.device()
            
            if isinstance(self.device_path, str):
                device_path_bytes = self.device_path.encode('utf-8')
            else:
                device_path_bytes = self.device_path
                
            self.device.open_path(device_path_bytes)
            
            print(f"Connected using path: {self.device_path}")
            return True
        except Exception as e:
            print(f"Failed to connect to working interface: {e}")
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
            
            if len(rgb_data) != self.num_leds * 3:
                if len(rgb_data) < self.num_leds * 3:
                    rgb_data.extend([0] * (self.num_leds * 3 - len(rgb_data)))
                else:
                    rgb_data = rgb_data[:self.num_leds * 3]
                    
                    
            packet.extend(rgb_data)
            packet.extend([0] * (520 - len(packet)))

            self.device.send_feature_report(packet)
            return True
        
        except Exception as e:
            print(f"Failed to send RGB data packet: {e}")
            return False
        
    def set_solid_color(self, r: int, g: int, b: int) -> bool:
        rgb_data = []
        for i in range(self.num_leds):
            rgb_data.extend([r, g, b])
        
        return self.send_rgb(rgb_data)
        
    
    def breathing_effect(self, r: int, g: int, b: int, duration: float = 10.0):
        import math
        
        if duration == 0:
            try:
                start_time = time.time()
                while True:
                    t = time.time() - start_time
                    brightness = (math.sin(t * 2) + 1) / 2
                
                    current_r = int(r * brightness)
                    current_g = int(g * brightness)
                    current_b = int(b * brightness)
                
                    self.set_solid_color(current_r, current_g, current_b)
                    time.sleep(0.05)
            except KeyboardInterrupt:
                self.turn_off()
                raise
                
            
        start_time = time.time()
        while time.time() - start_time < duration:
            t = time.time() - start_time
            brightness = (math.sin(t * 2) + 1) / 2
            
            current_r = int(r * brightness)
            current_g = int(g * brightness)
            current_b = int(b * brightness)
            
            self.set_solid_color(current_r, current_g, current_b)
            time.sleep(0.05)

    def test_sequence(self):
        print("Running test sequence...")
        
        print("Red...")
        self.set_solid_color(255, 0, 0)
        time.sleep(1)
        
        print("Green...")
        self.set_solid_color(0, 255, 0)
        time.sleep(1)
        
        print("Blue...")
        self.set_solid_color(0, 0, 255)
        time.sleep(1)
        
        print("Off...")
        self.set_solid_color(0, 0, 0)

    def turn_off(self):
        return self.set_solid_color(0, 0, 0)