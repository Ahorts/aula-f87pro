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
        if not devices:
            print("No Aula F87 Pro devices found.")
            return None

        for i, dev_info in enumerate(devices):
            if i == 0:  # Typically keyboard input interface
                print(f"Skipping interface {i} (likely keyboard input).")
                continue
            
            print(f"\nTesting interface {i}...")
            print(f"  Path: {dev_info['path']}")
            print(f"  Interface: {dev_info.get('interface_number', 'N/A')}")
            print(f"  Usage Page: {hex(dev_info.get('usage_page', 0))}")
            print(f"  Usage: {hex(dev_info.get('usage', 0))}")
            
            try:
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
            print(f"Verifying saved interface: {device_path}")
            device_path_bytes = device_path.encode('utf-8') if isinstance(device_path, str) else device_path
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
            print(f"Saved interface verification failed: {e}")
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
            device_path_bytes = self.device_path.encode('utf-8') if isinstance(self.device_path, str) else self.device_path
            self.device.open_path(device_path_bytes)
            print(f"Connected to Aula F87 Pro on path: {self.device_path}")
            return True
        except Exception as e:
            print(f"Failed to connect to working interface: {e}")
            self.device = None
            self.device_path = None
            return False
        
    def disconnect(self):
        if self.device:
            print("Disconnecting from keyboard.")
            self.device.close()
            self.device = None
            
    
    def send_rgb(self, rgb_data: list) -> bool:
        if not self.device:
            print("Error: Device not connected. Cannot send RGB data.")
            return False
        
        try:
            packet = [0x06, 0x08, 0x00, 0x00, 0x01, 0x00, 0x7A, 0x01]
            
            expected_len = self.num_leds * 3
            if len(rgb_data) != expected_len:
                if len(rgb_data) < expected_len:
                    rgb_data.extend([0] * (expected_len - len(rgb_data)))
                else:
                    rgb_data = rgb_data[:expected_len]
                                   
            packet.extend(rgb_data)
            packet.extend([0] * (520 - len(packet)))

            self.device.send_feature_report(packet)
            return True
        
        except hid.HIDException as e:
            print(f"HID Error: Failed to send RGB data packet: {e}")
            return False

        except Exception as e:
            print(f"Error: Failed to send RGB data packet: {e}")
            return False

    def turn_off(self) -> bool:
        """Turns all LEDs off."""
        print("Device: Turning all lights off.")
        rgb_data_off = [0] * (self.num_leds * 3)
        return self.send_rgb(rgb_data_off)
        
    def set_solid_color(self, r: int, g: int, b: int, duration: float = 0.0) -> bool:
        """
        Sets all LEDs to a solid color.
        If duration is 0.0 (default), the color is persistent until interrupted.
        If duration > 0.0, the color is set for that many seconds, then lights turn off.
        """
        print(f"Device: Setting solid color RGB({r},{g},{b}), duration: {'infinite' if duration == 0.0 else str(duration)+'s'}")
        rgb_data_initial = []
        for _ in range(self.num_leds):
            rgb_data_initial.extend([r, g, b])
        
        if not self.send_rgb(rgb_data_initial):
            print("Device Error: Failed to set initial solid color.")
            return False
        
        if duration == 0.0: 
            try:
                while True:
                    time.sleep(1) 
            except KeyboardInterrupt:
                print("\nDevice: Solid color effect interrupted by user.")
                self.turn_off()
                raise 
        else: #
            try:
                time.sleep(duration)
                print(f"Device: Solid color duration ({duration}s) ended.")
                self.turn_off()
            except KeyboardInterrupt:
                print("\nDevice: Timed solid color effect interrupted by user.")
                self.turn_off()
                raise 
        return True
        
    
    def breathing_effect(self, r: int, g: int, b: int, duration: float = 0.0):
        
        import math 
        print(f"Device: Breathing effect RGB({r},{g},{b}), duration: {'infinite' if duration == 0.0 else str(duration)+'s'}")

        try:
            start_time = time.time()
            while True:
                current_elapsed_time = time.time() - start_time
                
                if duration != 0.0 and current_elapsed_time >= duration:
                    print(f"Device: Breathing effect duration ({duration}s) ended.")
                    break 
                
                brightness_speed_factor = 1.5 
                brightness = (math.sin(current_elapsed_time * brightness_speed_factor) + 1) / 2

                current_r = int(r * brightness)
                current_g = int(g * brightness)
                current_b = int(b * brightness)
                
                frame_rgb_data = []
                for _ in range(self.num_leds):
                    frame_rgb_data.extend([current_r, current_g, current_b])
                
                if not self.send_rgb(frame_rgb_data):
                    print("Device Error: Failed to send frame for breathing effect. Stopping.")
                    break 
                
                time.sleep(0.05) 

        except KeyboardInterrupt:
            print("\nDevice: Breathing effect interrupted by user.")
            raise 
        finally:
            if duration > 0.0 and (time.time() - start_time >= duration): # Check if it completed naturally
                 self.turn_off()


    def test_sequence(self):
        print("Device: Running RGB test sequence...")
        colors_to_test = {
            "Red": (255, 0, 0), "Green": (0, 255, 0),
            "Blue": (0, 0, 255), "White": (255, 255, 255),
        }
        original_duration_behavior = True 
        
        for name, (r_val,g_val,b_val) in colors_to_test.items():
            print(f"Device Test: Setting color {name}")
            temp_rgb_data = []
            for _ in range(self.num_leds):
                temp_rgb_data.extend([r_val, g_val, b_val])
            if not self.send_rgb(temp_rgb_data):
                print(f"Device Test: Failed to set {name}")
                self.turn_off()
                return
            time.sleep(1) 
        
        print("Device Test: Turning lights off.")
        self.turn_off()
        print("Device Test: Sequence completed.")