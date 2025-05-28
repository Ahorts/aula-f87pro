import argparse
import sys
from .device import AulaF87Pro
from .colors import parse_color_input, predefined_colors

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
    parser.add_argument('--breathing', type=str,
                        help='Breathing effect with color (same formats as --color)')
    parser.add_argument('--duration', type=float, default=10.0,
                        help='Duration for breathing effect in seconds (default: 10)')
    
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
                if keyboard.set_solid_color(r, g, b):
                    print("Color set successfully.")
                else:
                    print("Failed to set color.")
                    return 1
            except ValueError as e:
                print(f"Error parsing color: {e}")
                return 1
        
        elif args.breathing:
            try:
                r, g, b = parse_color_input(args.breathing)
                print(f"Starting breathing effect: RGB({r}, {g}, {b}) for {args.duration} seconds...")
                keyboard.breathing_effect(r, g, b, args.duration)
                print("Breathing effect completed.")
            except ValueError as e:
                print(f"Error parsing color: {e}")
                return 1
            except KeyboardInterrupt:
                print("\nBreathing effect stopped.")
                keyboard.turn_off()
        
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