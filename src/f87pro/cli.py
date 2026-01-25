import argparse
import sys
import os
import time
import threading
from .device import AulaF87Pro
from .colors import parse_color_input, predefined_colors
from .pywal import load_wal_colors, WalFileWatcher

def create_parser():
    parser = argparse.ArgumentParser(
        description="Control the Aula F87 Pro RGB keyboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  aula-f87pro --color red
  aula-f87pro --color "#FF0000"
  aula-f87pro --color "255,0,0"
  aula-f87pro --breathing blue --duration 30
  aula-f87pro --pywal              # accent color from pywal
  aula-f87pro --pywal gradient     # gradient with pywal colors
  aula-f87pro --test
  aula-f87pro --off
  aula-f87pro --find-interface
        """
    )

     # Device connection options
    parser.add_argument('--find-interface', action='store_true',
                        help='Find and save the working RGB interface')
    parser.add_argument('--force-find', action='store_true',
                        help='Force re-detection of interface (ignore saved)')
    parser.add_argument('--show-config', action='store_true',
                        help='Show current saved configuration')
    
    # Color commands
    parser.add_argument('--color', type=str,
                        help='Set solid color (hex: #FF0000, RGB: 255,0,0, or name: red)')
    parser.add_argument('--breathing', nargs='?', const='__pywal__', default=None,
                        help='Breathing effect with color (same formats as --color). Color optional if --pywal is used.')
    parser.add_argument('--duration', type=float, default=10.0,
                        help='Duration for breathing effect in seconds (default: 10)')
    
    # Pywal integration
    parser.add_argument('--pywal', nargs='?', const='solid', default=None,
                        choices=['solid', 'gradient'],
                        help='Use pywal colors (solid=accent, gradient=row colors)')
    parser.add_argument('--watch', action='store_true',
                        help='Watch for changes in pywal colors and update automatically')

    # Utility commands
    parser.add_argument('--test', action='store_true',
                        help='Run RGB test sequence')
    parser.add_argument('--off', action='store_true',
                        help='Turn off all lighting')
    parser.add_argument('--list-colors', action='store_true',
                        help='List available predefined colors')
    
    return parser

def main():
    parser = create_parser()
    args = parser.parse_args()
    keyboard = AulaF87Pro()
    
    if args.list_colors:
        print("Available predefined colors:")
        colors = predefined_colors()
        for name, rgb in colors.items():
            print(f"  {name:<10} RGB{rgb}")
        return 0
    
    
    if args.show_config:
        keyboard.config_manager.show_config()
        return 0
    
    if args.find_interface:
        path = keyboard.find_working_interface()
        if path:
            print(f"\nWorking interface found and saved!")
            print("You can now use other commands.")
        else:
            print("No working interface found.")
            return 1
        return 0
    
    if not keyboard.connect(force_find=args.force_find):
        print("Failed to connect to keyboard.")
        print("\nYou need to run with Sudo or setup udev rules\n")
        print("Try running with --find-interface first to identify the working interface.")
        return 1
    
    try:
        if args.off:
            print("Turning off all lighting...")
            if keyboard.turn_off():
                print("Lighting turned off.")
            else:
                print("Failed to turn off lighting.")
                return 1
        
        elif args.test:
            keyboard.test_sequence()
            print("Test sequence completed.")
        
        elif args.color:
            try:
                r, g, b = parse_color_input(args.color)
                print(f"Setting solid color: RGB({r}, {g}, {b})")
                if keyboard.set_solid_color(r, g, b, args.duration):
                    print("Color set successfully.")
                else:
                    print("Failed to set color.")
                    return 1
            except ValueError as e:
                print(f"Error parsing color: {e}")
                return 1
        
        elif args.breathing or args.pywal:
            # State for watch mode - uses threading.Event for signaling
            change_event = threading.Event()
            stop_flag = threading.Event()
            
            # Callback for the file watcher
            def on_colors_changed():
                print("Pywal colors changed. Reloading...")
                change_event.set()
            
            # Start watcher if in watch mode
            watcher = None
            if args.watch:
                watcher = WalFileWatcher(on_change=on_colors_changed, debounce_seconds=1.0)
                watcher.start()
                print("Watching for pywal changes using inotify...")
            
            # Callback for effects to check if they should stop
            def should_stop_check():
                return change_event.is_set() or stop_flag.is_set()

            try:
                while True:
                    change_event.clear()
                    
                    # Load colors if potentially needed
                    colors = None
                    if args.pywal or (args.breathing == '__pywal__'):
                        colors = load_wal_colors()
                        if not colors and args.watch:
                            # If file disappears or is empty, wait and retry
                            time.sleep(1)
                            continue
                        elif not colors:
                            print("Error: Could not load pywal colors.")
                            return 1

                    # --- Breathing Logic ---
                    if args.breathing:
                        r, g, b = 0, 0, 0
                        base_data = None
                        if args.breathing == '__pywal__':
                            if args.pywal == 'gradient':
                                base_data = keyboard.create_gradient_data(colors)
                            else:
                                if len(colors) > 1: r, g, b = colors[1]
                                elif len(colors) > 0: r, g, b = colors[0]
                        else:
                            try:
                                r, g, b = parse_color_input(args.breathing)
                            except: pass 

                        if base_data:
                            print(f"Starting {'watched ' if args.watch else ''}breathing effect (Gradient)...")
                            keyboard.breathing_effect(0, 0, 0, args.duration if not args.watch else 0, base_rgb_data=base_data, should_stop=should_stop_check)
                        else:
                            print(f"Starting {'watched ' if args.watch else ''}breathing effect RGB({r},{g},{b})...")
                            keyboard.breathing_effect(r, g, b, args.duration if not args.watch else 0, should_stop=should_stop_check)

                    # --- Static Pywal Logic (if not breathing) ---
                    elif args.pywal:
                        if args.pywal == 'gradient':
                            print(f"Starting {'watched ' if args.watch else ''}pywal gradient...")
                            keyboard.set_pywal_gradient(colors, args.duration if not args.watch else 0, should_stop=should_stop_check)
                        else:
                            # Solid accent
                            if len(colors) > 1: r, g, b = colors[1]
                            elif len(colors) > 0: r, g, b = colors[0]
                            else: r,g,b = 255,255,255
                            
                            print(f"Starting {'watched ' if args.watch else ''}pywal solid RGB({r},{g},{b})...")
                            keyboard.set_solid_color(r, g, b, args.duration if not args.watch else 0, should_stop=should_stop_check)
                    
                    # If not watching, or we stopped for a reason other than file change, exit
                    if not args.watch or not change_event.is_set():
                        break
                    
            finally:
                if watcher:
                    watcher.stop()

        else:
            print("No command specified. Use --help for available options.")
            return 1
    
    except KeyboardInterrupt:
        print("\nOperation interrupted.")
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1
    finally:
        keyboard.disconnect()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())