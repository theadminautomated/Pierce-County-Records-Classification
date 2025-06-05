import sys
from app import _pick_directory

class DummyTk:
    def __init__(self):
        pass
    def withdraw(self):
        pass
    def destroy(self):
        pass

def test_pick_directory_no_tk(monkeypatch):
    monkeypatch.setitem(sys.modules, "tkinter", None)
    result = _pick_directory()
    assert result is None
