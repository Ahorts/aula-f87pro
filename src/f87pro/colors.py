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


def parse_rgb_string(rgb_string: str) -> Tuple[int, int, int]:
    try:
        values = [int(x.strip()) for x in rgb_string.split(',')]
        if len(values) != 3:
            raise ValueError("RGB string must have exactly 3 values")
        
        for value in values:
            if not 0 <= value <= 255:
                raise ValueError(f"RGB value {value} out of range 0-255")
        
        return (values[0], values[1], values[2])
    except ValueError as e:
        raise ValueError(f"Invalid RGB string '{rgb_string}': {e}")
    
    
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
        "orange": (255, 165, 0),
        "purple": (128, 0, 128),
        "pink": (255, 192, 203),
        "brown": (139, 69, 19),
    }

def get_color_by_name(name: str):
    colors = predefined_colors()
    return colors.get(name.lower())

def parse_color_input(color_input: str) -> Tuple[int, int, int]:
    color_input = color_input.strip()
    
    if color_input.startswith('#') or re.match(r'^[0-9a-fA-F]{6}$', color_input):
        return hex_to_rgb(color_input)
    
    if ',' in color_input:
        return parse_rgb_string(color_input)
    
    color = get_color_by_name(color_input)
    if color:
        return color
    
    raise ValueError(f"Invalid color format: {color_input}")