"""
Quick verification of theme helpers
"""

from RecordsClassifierGui.gui.theme import get_color, get_font, theme, layout, colors, typography

print("Theme module verification:")
print(f"Background: {get_color('bg')}")
print(f"Default font: {get_font()}")
print(f"Heading font: {get_font('heading')}")
print(f"Layout keys: {list(layout.keys())}")
print(f"Colors keys: {list(colors.keys())}")
print(f"Typography keys: {list(typography.keys())}")
print("All helpers loaded successfully!")
