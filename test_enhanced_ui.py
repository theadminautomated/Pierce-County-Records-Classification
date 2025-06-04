#!/usr/bin/env python3
"""
Test script for the enhanced Records Classifier GUI implementation.
This script validates that all the UI enhancements are working correctly.
"""

import sys
import os

# Add the RecordsClassifierGui directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'RecordsClassifierGui'))

try:
    print("Testing enhanced UI implementation...")
    print("=" * 50)
      # Test 1: Import theme module
    print("1. Testing theme module import...")
    try:
        from RecordsClassifierGui.gui.theme import theme, layout, colors, typography
        print("   ✓ Theme module imported successfully")
        print(f"   ✓ Theme contains {len(theme)} keys")
        print(f"   ✓ Layout contains {len(layout)} keys")
        print(f"   ✓ Colors contains {len(colors)} keys")
    except Exception as e:
        print(f"   ✗ Theme import failed: {e}")
        
    # Test 2: Import screens module
    print("\n2. Testing screens module import...")
    try:
        from RecordsClassifierGui.gui.screens import MainScreen, SetupScreen
        print("   ✓ Screens module imported successfully")
        print("   ✓ MainScreen class available")
        print("   ✓ SetupScreen class available")
    except Exception as e:
        print(f"   ✗ Screens import failed: {e}")
        
    # Test 3: Import app module
    print("\n3. Testing app module import...")
    try:
        from RecordsClassifierGui.gui.app import RecordsClassifierApp
        print("   ✓ App module imported successfully")
        print("   ✓ RecordsClassifierApp class available")
    except Exception as e:
        print(f"   ✗ App import failed: {e}")
        
    # Test 4: Test MainScreen instantiation
    print("\n4. Testing MainScreen instantiation...")
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        
        # Create MainScreen instance
        main_screen = MainScreen(root)
        print("   ✓ MainScreen created successfully")
        
        # Check if key methods exist
        methods_to_check = [
            '_setup_header', '_setup_path_selection', '_setup_controls',
            '_setup_results_table', '_setup_status_bar', '_setup_keyboard_shortcuts',
            '_validate_folder_path', '_validate_output_path', '_update_stats',
            '_sort_table', '_bulk_export', '_toggle_classification'
        ]
        
        for method in methods_to_check:
            if hasattr(main_screen, method):
                print(f"   ✓ Method {method} exists")
            else:
                print(f"   ✗ Method {method} missing")
                
        root.destroy()
        
    except Exception as e:
        print(f"   ✗ MainScreen instantiation failed: {e}")
        
    # Test 5: Test theme integration
    print("\n5. Testing theme integration...")
    try:
        from RecordsClassifierGui.gui.theme import get_color, get_font
        
        # Test color retrieval
        bg_color = get_color('bg')
        fg_color = get_color('fg')
        print(f"   ✓ Background color: {bg_color}")
        print(f"   ✓ Foreground color: {fg_color}")
          # Test font retrieval
        default_font = get_font()
        heading_font = get_font(key='heading')
        print(f"   ✓ Default font: {default_font}")
        print(f"   ✓ Heading font: {heading_font}")
        
    except Exception as e:
        print(f"   ✗ Theme integration test failed: {e}")
        
    print("\n" + "=" * 50)
    print("Enhanced UI implementation test completed!")
    print("If all tests passed, the UI enhancements are ready for use.")
    
except Exception as e:
    print(f"Critical error during testing: {e}")
    sys.exit(1)
