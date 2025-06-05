"""Streamlit entrypoint with live progress and stats."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd
import streamlit as st
from streamlit.logger import get_logger

from RecordsClassifierGui.logic.classification_engine_fixed import (
    ClassificationEngine,
    classify_directory,
    ClassificationResult,
)
from config import CONFIG
from version import __version__
from streamlit_helpers import load_file_content, compute_stats

logger = get_logger(__name__)


@st.cache_resource
def get_engine() -> ClassificationEngine:
    """Create or return the cached engine."""
    return ClassificationEngine()


def _append_result(result: ClassificationResult) -> None:
    """Store a classification result for later display."""
    st.session_state.setdefault("results", [])
    st.session_state["results"].append(
        {
            "File": result.file_name,
            "Size": result.size_kb,
            "Modified": result.last_modified,
            "Classification": result.model_determination,
            "Confidence": result.confidence_score,
            "Status": result.status,
            "Contextual Insights": result.contextual_insights,
            "File Path": result.full_path,
        }
    )


def _update_table(placeholder: st.delta_generator.DeltaGenerator) -> None:
    """Render results in the given placeholder."""
    df = pd.DataFrame(st.session_state.get("results", []))
    if df.empty:
        placeholder.empty()
        return
    placeholder.dataframe(df, use_container_width=True)
    st.session_state["stats"] = compute_stats(st.session_state["results"])


def _process_paths(
    paths: Iterable[Path],
    engine: ClassificationEngine,
    mode: str,
    years: int | None,
    table_ph: st.delta_generator.DeltaGenerator,
) -> None:
    """Classify provided paths and update the table live."""
    paths = list(paths)
    progress = st.progress(0)
    for idx, path in enumerate(paths, start=1):
        with st.spinner(f"Processing {path.name}"):
            try:
                result = engine.classify_file(path, run_mode=mode, threshold_years=years or 6)
            except Exception as exc:  # pragma: no cover - UI feedback only
                logger.exception("Classification failed")
                st.error(f"Failed to classify {path.name}: {exc}")
                continue
        _append_result(result)
        _update_table(table_ph)
        progress.progress(idx / len(paths))
    progress.empty()


def _run_folder(
    path: Path,
    engine: ClassificationEngine,
    mode: str,
    years: int | None,
    table_ph: st.delta_generator.DeltaGenerator,
) -> None:
    """Classify every supported file in ``path`` recursively."""
    if not path.exists() or not path.is_dir():
        st.error("Folder does not exist")
        return

    results = classify_directory(path, engine=engine, run_mode=mode, threshold_years=years or 6)
    for res in results:
        _append_result(res)
        _update_table(table_ph)


def _show_stats() -> None:
    """Display summary metrics in the footer."""
    stats = st.session_state.get("stats")
    if not stats:
        return
    cols = st.columns(4)
    cols[0].metric("Processed", stats["total"])
    cols[1].metric("Success", stats["success"])
    cols[2].metric("Skipped", stats["skipped"])
    cols[3].metric("Errors", stats["error"])



def main() -> None:
    """Run the Streamlit UI."""
    st.set_page_config(page_title="Records Classifier", page_icon="📄", layout="wide")
    st.sidebar.title("Pierce County Records Classifier")
    st.sidebar.write(f"Version {__version__}")

    engine = get_engine()

    mode = st.sidebar.radio(
        "Mode",
        options=["Classification", "Last Modified"],
        help="Choose 'Classification' to analyze a document or 'Last Modified' to auto-destroy old files.",
    )

    years: int | None = None
    if mode == "Last Modified":
        years = st.sidebar.slider(
            "Last Modified Threshold (years)",
            1,
            10,
            6,
            help="Files older than this will be classified as DESTROY.",
        )

    st.title("Electronic Records Classifier")
    st.write(f"Model: {CONFIG.model_name}")

    uploads = st.file_uploader(
        "Upload files",
        accept_multiple_files=True,
        help="Supported formats: PDF, DOCX, images, etc.",
    )

    table_ph = st.empty()

    if uploads:
        paths: list[Path] = []
        for file in uploads:
            p = load_file_content(file)
            if p:
                paths.append(p)
        _process_paths(paths, engine, mode, years, table_ph)

    folder = st.text_input("Or enter a folder path to scan")
    if folder and st.button("Scan Folder"):
        _run_folder(Path(folder), engine, mode, years, table_ph)

    _update_table(table_ph)
    _show_stats()


if __name__ == "__main__":
    main()
