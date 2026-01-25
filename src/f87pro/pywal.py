import os
from pathlib import Path
from typing import List, Tuple, Optional

def get_wal_colors_path() -> Path:
    """Get the path to pywal colors file."""
    return Path.home() / ".cache" / "wal" / "colors"

def parse_hex_color(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.strip().lstrip('#')
    return (
        int(hex_color[0:2], 16),
        int(hex_color[2:4], 16),
        int(hex_color[4:6], 16)
    )

def load_wal_colors() -> Optional[List[Tuple[int, int, int]]]:
    """Load colors from pywal cache."""
    colors_path = get_wal_colors_path()

    if not colors_path.exists():
        return None

    colors = []
    with open(colors_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and line.startswith('#'):
                try:
                    colors.append(parse_hex_color(line))
                except (ValueError, IndexError):
                    continue

    return colors if colors else None

def get_accent_color() -> Optional[Tuple[int, int, int]]:
    """Get the accent color (usually color 1 or brightest)."""
    colors = load_wal_colors()
    if not colors or len(colors) < 2:
        return None
    # Color 1 is typically the primary accent
    return colors[1]

def get_background_color() -> Optional[Tuple[int, int, int]]:
    """Get the background color (color 0)."""
    colors = load_wal_colors()
    if not colors:
        return None
    return colors[0]

def check_file_changed(initial_mtime: float, path_str: str) -> bool:
    """Check if file modification time has changed."""
    try:
        current_mtime = os.stat(path_str).st_mtime
        return current_mtime != initial_mtime
    except OSError:
        return False

def get_wal_file_mtime() -> float:
    """Get the current mtime of the wal colors file."""
    path = get_wal_colors_path()
    if path.exists():
         return os.stat(str(path)).st_mtime
    return 0

def get_foreground_color() -> Optional[Tuple[int, int, int]]:
    """Get the foreground color (color 7 or 15)."""
    colors = load_wal_colors()
    if not colors:
        return None
    # Color 7 is typically foreground
    if len(colors) > 7:
        return colors[7]
    return colors[-1]
