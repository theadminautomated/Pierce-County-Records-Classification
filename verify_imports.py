#!/usr/bin/env python3
"""
Verification file to confirm that all import errors are resolved.
"""

import sys
import os
import importlib

# Add the RecordsClassifierGui directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'RecordsClassifierGui'))

def check_import(import_path, objects=None):
    """Check if an import path works and optionally verify specific objects."""
    try:
        module = importlib.import_module(import_path)
        print(f"✓ Successfully imported: {import_path}")
        
        if objects:
            for obj in objects:
                if hasattr(module, obj):
                    print(f"  ✓ Object '{obj}' exists in {import_path}")
                else:
                    print(f"  ✗ Object '{obj}' missing from {import_path}")
        return True
    except ImportError as e:
        print(f"✗ Failed to import: {import_path}")
        print(f"  Error: {e}")
        return False

# Test all relevant imports
print("Testing all relevant imports...")
print("=" * 50)

# Theme module and its components
check_import("RecordsClassifierGui.gui.theme", ["theme", "layout", "colors", "typography", "get_color", "get_font"])

# Screens module and classes
check_import("RecordsClassifierGui.gui.screens", ["MainScreen", "SetupScreen"])

# App module and its components
check_import("RecordsClassifierGui.gui.app", ["RecordsClassifierApp"])

print("=" * 50)
print("Import verification completed!")
