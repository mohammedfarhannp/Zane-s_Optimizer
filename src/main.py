"""
Zane's Optimizer Version 1.0 (Experimental)

Academic Image Layout Tool
Automatically arranges multiple images optimally on A4 PDF pages
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow

def main():
    try:
        # Create and run the application
        app = MainWindow()
        app.run()
        
    except Exception as e:
        print(f"\n Error starting application: {e}")
        input("\nPress Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()