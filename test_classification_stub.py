import tempfile
import os
import datetime
import tempfile
from pathlib import Path
from RecordsClassifierGui.logic.classification_engine_fixed import (
    ClassificationEngine,
    classify_directory,
)


def test_classify_file_stub():
    engine = ClassificationEngine(timeout_seconds=1)
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as tf:
        tf.write("sample text")
        path = Path(tf.name)
    try:
        result = engine.classify_file(path)
        assert result.model_determination in {"TRANSITORY", "DESTROY", "KEEP"}
        assert result.status
        assert result.full_path == str(path.resolve())
    finally:
        path.unlink(missing_ok=True)


def test_last_modified_mode_auto_destroy(tmp_path):
    engine = ClassificationEngine(timeout_seconds=1)
    file_path = tmp_path / "old.txt"
    file_path.write_text("old content")
    old_time = (
        datetime.datetime.now() - datetime.timedelta(days=6 * 365 + 1)
    ).timestamp()
    os.utime(file_path, (old_time, old_time))
    result = engine.classify_file(file_path, run_mode="Last Modified")
    assert result.model_determination == "DESTROY"


def test_last_modified_custom_threshold(tmp_path):
    engine = ClassificationEngine(timeout_seconds=1)
    file_path = tmp_path / "three_years.txt"
    file_path.write_text("content")
    old_time = (
        datetime.datetime.now() - datetime.timedelta(days=3 * 365 + 1)
    ).timestamp()
    os.utime(file_path, (old_time, old_time))

    result = engine.classify_file(
        file_path, run_mode="Last Modified", threshold_years=2
    )
    assert result.model_determination == "DESTROY"


def test_skip_returns_na(tmp_path):
    engine = ClassificationEngine(timeout_seconds=1)
    file_path = tmp_path / "foo.exe"
    file_path.write_text("bin")
    result = engine.classify_file(file_path)
    assert result.model_determination == "NA"
    assert result.status == "skipped"


def test_old_file_destroy_even_if_skipped(tmp_path):
    engine = ClassificationEngine(timeout_seconds=1)
    file_path = tmp_path / "old.exe"
    file_path.write_text("bin")
    old_time = (
        datetime.datetime.now() - datetime.timedelta(days=6 * 365 + 1)
    ).timestamp()
    os.utime(file_path, (old_time, old_time))
    result = engine.classify_file(file_path)
    assert result.model_determination == "DESTROY"


def test_classify_directory_generator(tmp_path):
    engine = ClassificationEngine(timeout_seconds=1)
    # create multiple small files
    for i in range(5):
        (tmp_path / f"f{i}.txt").write_text("hello")

    results = list(
        classify_directory(tmp_path, engine=engine, run_mode="Classification")
    )
    assert len(results) == 5
    assert all(r.model_determination for r in results)


def test_last_modified_skip_returns_na(tmp_path):
    engine = ClassificationEngine(timeout_seconds=1)
    file_path = tmp_path / "recent.txt"
    file_path.write_text("hi")
    result = engine.classify_file(file_path, run_mode="Last Modified")
    assert result.model_determination == "NA"
    assert result.status == "skipped"
