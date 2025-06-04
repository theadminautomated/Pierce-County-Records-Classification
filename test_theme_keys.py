"""
Test that the RecordsClassifierGui can be initialized without theme key errors.
"""

import pytest
import sys
import os

pytest.importorskip("psutil")

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_theme_keys():
    """Test that all required theme keys are present or have fallbacks."""
    from RecordsClassifierGui.gui.theme import theme
    from RecordsClassifierGui.gui.RecordsClassifierGui import ensure_theme_keys
    
    # First run without ensuring keys
    assert 'bg' in theme
    
    # Test ensure_theme_keys function
    ensure_theme_keys()
    
    # Verify statusbar keys exist after calling ensure_theme_keys
    assert 'statusbar_bg' in theme
    assert 'statusbar_fg' in theme
    
    # Check that the values are correct
    assert theme['statusbar_bg'] == theme.get('status_bg', theme.get('bg', '#1e1e1e'))
    assert theme['statusbar_fg'] == theme.get('fg', '#e0e0e0')

if __name__ == "__main__":
    test_theme_keys()
    print("All tests passed!")
