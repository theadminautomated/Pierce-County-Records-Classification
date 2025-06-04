#!/usr/bin/env python3
"""
Simple demo script to showcase the enhanced MainScreen implementation.
This script launches the MainScreen directly for testing and demonstration.
"""

import sys
import os
import tkinter as tk

# Add the RecordsClassifierGui directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'RecordsClassifierGui'))

try:
    import customtkinter as ctk
    from gui.screens import MainScreen
    from gui.theme import theme
    
    print("🚀 Launching Enhanced Records Classifier MainScreen Demo...")
    print("=" * 60)
    
    # Configure CustomTkinter
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Create main window
    root = ctk.CTk()
    root.title("Pierce County Records Classifier - Enhanced UI Demo")
    root.geometry("1400x900")
    root.configure(fg_color=theme['bg'])
    
    print("✓ Main window created")
    
    # Create and display MainScreen
    main_screen = MainScreen(root)
    main_screen.pack(fill="both", expand=True)
    
    print("✓ MainScreen initialized with enhanced features:")
    print("  • Modern header with branding and quick stats")
    print("  • Enhanced path selection with real-time validation")
    print("  • Advanced controls with parallel jobs slider")
    print("  • Sophisticated results table with bulk operations")
    print("  • Modern status bar with real-time statistics")
    print("  • Comprehensive keyboard shortcuts")
    print("  • Focus handlers and enhanced UX")
    print("  • Mock processing simulation")
    print("  • Table sorting and context menus")
    print("  • Bulk operations (RERUN, EXPORT, DESTROY)")
    
    print("\n📋 Available Keyboard Shortcuts:")
    print("  • Ctrl+O: Browse input folder")
    print("  • Ctrl+S: Browse output file")
    print("  • Ctrl+R: Start/Stop classification")
    print("  • Ctrl+A: Select/Deselect all")
    print("  • Delete: Remove selected items")
    print("  • Ctrl+E: Export selected items")
    print("  • Ctrl+T: Toggle theme")
    print("  • F5: Refresh table")
    print("  • Escape: Clear selection")
    
    print("\n🎯 UI Features Demonstrated:")
    print("  • Modern glassmorphism design")
    print("  • Responsive layout with proper grid management")
    print("  • Real-time path validation with visual feedback")
    print("  • Advanced table with extended columns and color-coding")
    print("  • Parallel processing controls")
    print("  • Comprehensive error handling")
    print("  • Accessibility features and tooltips")
    
    print("\n🌟 The enhanced UI is now ready for use!")
    print("=" * 60)
    
    # Start the application
    root.mainloop()
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all required dependencies are installed.")
except Exception as e:
    print(f"❌ Error launching demo: {e}")
    import traceback
    traceback.print_exc()
