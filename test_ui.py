#!/usr/bin/env python
"""
Simple test script to verify the UI loads correctly
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
script_dir = Path(__file__).resolve().parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

# Add the RecordsClassifierGui package directory to Python path
package_dir = script_dir / 'RecordsClassifierGui'
if str(package_dir) not in sys.path:
    sys.path.insert(0, str(package_dir))

try:
    print("Testing imports...")
    from RecordsClassifierGui.gui.app import RecordsClassifierApp
    print("✓ RecordsClassifierApp imported successfully")
    
    print("Testing MainScreen import...")
    from RecordsClassifierGui.gui.screens import MainScreen
    print("✓ MainScreen imported successfully")
    
    print("Testing theme import...")
    from RecordsClassifierGui.gui.theme import theme
    print("✓ Theme imported successfully")
    print(f"✓ Theme has {len(theme)} keys")
    
    print("Creating app instance...")
    app = RecordsClassifierApp()
    print("✓ App created successfully")
    
    print("All tests passed! The UI should work correctly.")
    
    # Start the app
    print("Starting application...")
    app.mainloop()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
