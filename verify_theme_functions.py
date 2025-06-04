#!/usr/bin/env python3
"""
Verify the theme functions are working correctly.
"""

import sys
import os

# Add the RecordsClassifierGui directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'RecordsClassifierGui'))

try:
    print("Testing theme functions...")
    print("=" * 50)
    
    from RecordsClassifierGui.gui.theme import get_color, get_font, theme, layout, colors, typography
    
    # Test color retrieval
    print("\nColor retrieval:")
    print(f"- Background: {get_color('bg')}")
    print(f"- Foreground: {get_color('fg')}")
    print(f"- Accent: {get_color('accent')}")
    print(f"- Missing with default: {get_color('nonexistent', '#default')}")
    
    # Test font retrieval
    print("\nFont retrieval:")
    print(f"- Default font: {get_font()}")
    print(f"- Heading font: {get_font('heading')}")
    print(f"- Title font: {get_font('title')}")
    print(f"- Default with size: {get_font(size=18)}")
    print(f"- Heading with size: {get_font('heading', 20)}")
    
    print("\nTheme object contents:")
    print(f"- Total keys: {len(theme)}")
    print(f"- Sample keys: {list(theme.keys())[:5]}")
    
    print("\nLayout object contents:")
    print(f"- Total keys: {len(layout)}")
    print(f"- All keys: {list(layout.keys())}")
    
    print("\nColors object contents:")
    print(f"- Total keys: {len(colors)}")
    print(f"- All keys: {list(colors.keys())}")
    
    print("\nTypography object contents:")
    print(f"- Total keys: {len(typography)}")
    print(f"- All keys: {list(typography.keys())}")
    
    print("\n" + "=" * 50)
    print("Theme functions test completed!")
    
except Exception as e:
    print(f"Critical error during testing: {e}")
    sys.exit(1)
