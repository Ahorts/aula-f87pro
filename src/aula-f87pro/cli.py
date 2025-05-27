import argparse
from device import AulaF87Pro

def main():
    parser = argparse.ArgumentParser(description="Control the Aula F87 Pro RGB keyboard.")
    parser.add_argument('--color', type=str, help='Set the keyboard color in HEX or RGB format (e.g., #FF5733 or 255,87,51).')
    
    args = parser.parse_args()
    
    keyboard = AulaF87Pro()
    
    