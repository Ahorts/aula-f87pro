import argparse
from device import AulaF87Pro
from colors import parse_color_input, predefined_colors

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