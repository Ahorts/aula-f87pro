#!/usr/bin/env python3
import sys
import os

# Add the package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from f87pro.cli import main

if __name__ == "__main__":
    sys.exit(main())