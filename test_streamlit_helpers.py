from pathlib import Path
import tempfile
from streamlit_helpers import sanitize_filename, load_file_content, compute_stats

class DummyUpload:
    def __init__(self, name: str, data: bytes):
        self.name = name
        self._data = data
    def read(self):
        return self._data


def test_sanitize_filename():
    assert sanitize_filename('..\\evil.txt') == 'evil.txt'


def test_load_file_content(tmp_path: Path):
    dummy = DummyUpload('demo.txt', b'hi')
    # simulate session state
    import streamlit as st
    st.session_state['temp_dir'] = str(tmp_path)
    path = load_file_content(dummy)
    assert path is not None
    assert path.read_bytes() == b'hi'


def test_compute_stats():
    data = [
        {"Classification": "KEEP", "Status": "success"},
        {"Classification": "DESTROY", "Status": "success"},
        {"Classification": "NA", "Status": "skipped"},
        {"Classification": "TRANSITORY", "Status": "error"},
    ]
    stats = compute_stats(data)
    assert stats["total"] == 4
    assert stats["keep"] == 1
    assert stats["destroy"] == 1
    assert stats["na"] == 1
    assert stats["transitory"] == 1
    assert stats["success"] == 2
    assert stats["skipped"] == 1
    assert stats["error"] == 1
