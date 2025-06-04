"""Modern Streamlit UI for the Pierce County Records Classifier."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable

import pandas as pd
import streamlit as st

from RecordsClassifierGui.logic.classification_engine_fixed import (
    ClassificationEngine,
    classify_directory,
    ClassificationResult,
)
from config import CONFIG
from version import __version__
from streamlit_helpers import load_file_content

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


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


def _process_paths(paths: Iterable[Path], engine: ClassificationEngine, mode: str, years: int | None) -> None:
    """Classify all paths and update the results table."""
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
        progress.progress(idx / len(paths))
    progress.empty()


def _run_folder(path: Path, engine: ClassificationEngine, mode: str, years: int | None) -> None:
    """Classify every supported file in ``path``."""
    if not path.exists() or not path.is_dir():
        st.error("Folder does not exist")
        return

    results = classify_directory(path, engine=engine, run_mode=mode, threshold_years=years or 6)
    for res in results:
        _append_result(res)


def _show_table() -> None:
    """Display results with filtering and export options."""
    if "results" not in st.session_state:
        return
    df = pd.DataFrame(st.session_state["results"])

    with st.expander("Filters", expanded=False):
        classes = st.multiselect("Classification", options=df["Classification"].unique(), default=list(df["Classification"].unique()))
        status = st.multiselect("Status", options=df["Status"].unique(), default=list(df["Status"].unique()))
        min_conf = st.slider("Minimum Confidence", 0, 100, 0)
        filtered = df[df["Classification"].isin(classes) & df["Status"].isin(status) & (df["Confidence"] >= min_conf)]
    st.dataframe(filtered, use_container_width=True)

    csv = filtered.to_csv(index=False).encode()
    st.download_button("Export to CSV", csv, file_name="results.csv", mime="text/csv")

    st.write(f"Processed: {len(df)} files | Displaying: {len(filtered)}")


def show_about() -> None:
    """Display sidebar info."""
    st.sidebar.markdown(
        f"**Pierce County Records Classifier**\n\nVersion: {__version__}\n\n"
        "For help contact: records-support@example.com"
    )


def main() -> None:
    """Run the Streamlit UI."""
    st.set_page_config(page_title="Records Classifier", page_icon="📄", layout="wide")
    show_about()
    st.title("Pierce County Electronic Records Classifier")
    st.write(f"Model: {CONFIG.model_name}")

    engine = ClassificationEngine()

    mode = st.radio(
        "Mode",
        options=["Classification", "Last Modified"],
        horizontal=True,
        help="Choose 'Classification' to analyze a document or 'Last Modified' to auto-destroy old files.",
    )

    years: int | None = None
    if mode == "Last Modified":
        years = st.slider(
            "Last Modified Threshold (years)",
            1,
            10,
            6,
            help="Files older than this will be classified as DESTROY.",
        )

    uploads = st.file_uploader(
        "Upload files",
        accept_multiple_files=True,
        help="Supported formats: PDF, DOCX, images, etc.",
    )
    if uploads:
        paths: list[Path] = []
        for file in uploads:
            p = load_file_content(file)
            if p:
                paths.append(p)
        _process_paths(paths, engine, mode, years)

    folder = st.text_input("Or enter a folder path to scan")
    if folder and st.button("Scan Folder"):
        _run_folder(Path(folder), engine, mode, years)

    _show_table()


if __name__ == "__main__":
    main()
