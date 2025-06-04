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
    assert result.contextual_insights == "Older than 6 years - automatic destroy"


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
    assert result.contextual_insights == "Older than 6 years - automatic destroy"


def test_auto_destroy_context(tmp_path):
    engine = ClassificationEngine(timeout_seconds=1)
    file_path = tmp_path / "very_old.txt"
    file_path.write_text("data")
    old_time = (
        datetime.datetime.now() - datetime.timedelta(days=6 * 365 + 2)
    ).timestamp()
    os.utime(file_path, (old_time, old_time))
    result = engine.classify_file(file_path)
    assert result.model_determination == "DESTROY"
    assert result.contextual_insights == "Older than 6 years - automatic destroy"


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


def test_classify_directory_includes_old(tmp_path):
    engine = ClassificationEngine(timeout_seconds=1)
    old_file = tmp_path / "old.txt"
    old_file.write_text("abc")
    old_time = (
        datetime.datetime.now() - datetime.timedelta(days=6 * 365 + 3)
    ).timestamp()
    os.utime(old_file, (old_time, old_time))

    results = list(classify_directory(tmp_path, engine=engine))
    assert any(r.file_name == "old.txt" and r.model_determination == "DESTROY" for r in results)


def test_last_modified_skip_returns_na(tmp_path):
    engine = ClassificationEngine(timeout_seconds=1)
    file_path = tmp_path / "recent.txt"
    file_path.write_text("hi")
    result = engine.classify_file(file_path, run_mode="Last Modified")
    assert result.model_determination == "NA"
    assert result.status == "skipped"


def test_transitory_when_no_keywords(tmp_path):
    engine = ClassificationEngine(timeout_seconds=1)
    file_path = tmp_path / "plain.txt"
    file_path.write_text("just some random words")
    result = engine.classify_file(file_path)
    assert result.model_determination == "TRANSITORY"
    assert "No Schedule 6 keywords" in result.contextual_insights


def test_binary_snippet_placeholder(tmp_path):
    engine = ClassificationEngine(timeout_seconds=1)
    file_path = tmp_path / "bin.txt"
    file_path.write_bytes(b"\x00\x01\x02" * 50)
    result = engine.classify_file(file_path)
    assert "[File is binary or unreadable]" in result.contextual_insights
