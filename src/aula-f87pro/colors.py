from typing import Dict, Tuple
import re

def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    hex_color = hex_color.lstrip('#')

    if len(hex_color) not in [6,8]:
        raise ValueError("Invalid hex color format. Must be 6 characters long.")
   
    hex_color = hex_color[:6] 

    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b)

    except ValueError:
        raise ValueError(f"Invalid hex color: {hex_color}")

def rgb_to_hex(rgb_color: Tuple[int, int, int]) -> str:
    if len(rgb_color) != 3:
        raise ValueError("RGB color must have exactly 3 components")
    
    for component in rgb_color:
        if not 0 <= component <= 255:
            raise ValueError(f"RGB component {component} out of range 0-255")
    
    return '#{:02x}{:02x}{:02x}'.format(*rgb_color)

def validate_rgb(rgb_color: Tuple[int, int, int]) -> bool:
    return all(0 <= c <= 255 for c in rgb_color)    

def predefined_colors() -> Dict[str, Tuple[int, int, int]]:
    return {
        "red": (255, 0, 0),
        "green": (0, 255, 0),
        "blue": (0, 0, 255),
        "white": (255, 255, 255),
        "black": (0, 0, 0),
        "yellow": (255, 255, 0),
        "cyan": (0, 255, 255),
        "magenta": (255, 0, 255),
    }