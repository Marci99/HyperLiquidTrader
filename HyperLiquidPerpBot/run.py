#!/usr/bin/env python3
"""
HyperLiquidPerpBot launcher script
"""

import os
import sys

# Add parent directory to path to ensure imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the main application
from app.main import main

if __name__ == "__main__":
    main()