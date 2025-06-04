from RecordsClassifierGui.gui.theme import get_font

print("Testing get_font function:")
print(f"Default font: {get_font()}")
print(f"Default font with named arg: {get_font(key=None)}")
print(f"Heading font: {get_font(key='heading')}")
