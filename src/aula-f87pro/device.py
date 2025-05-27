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