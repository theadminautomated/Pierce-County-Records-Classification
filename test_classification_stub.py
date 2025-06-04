import tempfile
from pathlib import Path
from RecordsClassifierGui.logic.classification_engine_fixed import ClassificationEngine

def test_classify_file_stub():
    engine = ClassificationEngine(timeout_seconds=1)
    with tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False) as tf:
        tf.write('sample text')
        path = Path(tf.name)
    try:
        result = engine.classify_file(path)
        assert result.model_determination in {'TRANSITORY', 'DESTROY', 'KEEP'}
        assert result.status
    finally:
        path.unlink(missing_ok=True)
