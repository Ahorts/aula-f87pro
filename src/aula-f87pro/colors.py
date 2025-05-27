from typing import Dict, Tuple

def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        raise ValueError("Invalid hex color format. Must be 6 characters long.")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (r, g, b)

def rgb_to_hex(rgb_color: Tuple[int, int, int]) -> str:
    if any(not (0 <= c <= 255) for c in rgb_color):
        raise ValueError("RGB values must be between 0 and 255.")
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