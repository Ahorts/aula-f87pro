class AulaF87Pro:
    VENDOR_ID = 0x258a
    PRODUCT_ID = 0x010c
    
    def __init__(self):
        self.device = None
        self.device_path = None
    
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
        
    
    
