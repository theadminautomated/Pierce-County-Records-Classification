import tempfile
from pathlib import Path
from RecordsClassifierGui.logic.file_scanner import extract_file_content, _clean_text


def test_extract_txt():
    text = "Hello\nWorld\n"
    with tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False) as tf:
        tf.write(text)
        temp_path = Path(tf.name)
    try:
        result = extract_file_content(temp_path)
        assert result == "Hello\nWorld"
    finally:
        temp_path.unlink(missing_ok=True)


def test_extract_doc_missing_antiword():
    with tempfile.NamedTemporaryFile('w', suffix='.doc', delete=False) as tf:
        tf.write('dummy')
        path = Path(tf.name)
    try:
        result = extract_file_content(path)
        assert "[antiword not installed" in result
    finally:
        path.unlink(missing_ok=True)

