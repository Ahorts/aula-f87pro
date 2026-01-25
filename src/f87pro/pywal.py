import os
import threading
from pathlib import Path
from typing import List, Tuple, Optional, Callable

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


class WalFileWatcher:
    """
    Watch pywal colors file for changes using inotify (event-based, efficient).
    Requires the 'inotify' package: pip install inotify
    """
    
    def __init__(self, on_change: Callable[[], None], debounce_seconds: float = 1.0):
        self.on_change = on_change
        self.debounce_seconds = debounce_seconds
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._last_colors: Optional[List[Tuple[int, int, int]]] = None
        
        # Import inotify - fail loudly if not available
        try:
            import inotify.adapters
            self._inotify = inotify.adapters
        except ImportError:
            raise ImportError(
                "The 'inotify' package is required for --watch mode.\n"
                "Install it with: pip install inotify\n"
                "Or if using pipx: pipx inject aula-f87pro-cli inotify"
            )
    
    def _colors_changed(self) -> bool:
        """Check if colors actually changed (not just mtime)."""
        new_colors = load_wal_colors()
        if new_colors != self._last_colors:
            self._last_colors = new_colors
            return True
        return False
    
    def _watch_inotify(self):
        """Watch using inotify (efficient, no polling)."""
        wal_path = get_wal_colors_path()
        wal_dir = str(wal_path.parent)
        wal_filename = wal_path.name
        
        i = self._inotify.Inotify()
        i.add_watch(wal_dir)
        
        # Initialize last colors
        self._last_colors = load_wal_colors()
        
        for event in i.event_gen(yield_nones=False):
            if self._stop_event.is_set():
                break
                
            (_, type_names, path, filename) = event
            
            # Check if it's our file and a write/move event
            if filename == wal_filename and any(t in type_names for t in ['IN_CLOSE_WRITE', 'IN_MOVED_TO']):
                # Debounce
                import time
                time.sleep(self.debounce_seconds)
                
                if self._stop_event.is_set():
                    break
                
                # Only trigger if colors actually changed
                if self._colors_changed():
                    self.on_change()
        
        i.remove_watch(wal_dir)
    
    def start(self):
        """Start watching in a background thread."""
        if self._thread and self._thread.is_alive():
            return
        
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._watch_inotify, daemon=True)
        self._thread.start()
    
    def stop(self):
        """Stop watching."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2.0)
        return self._use_inotify
