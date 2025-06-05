"""Streamlit entrypoint with live progress and stats."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st
from streamlit.logger import get_logger
from RecordsClassifierGui.logic.file_scanner import FileScanner

from RecordsClassifierGui.logic.classification_engine_fixed import (
    ClassificationEngine,
    classify_directory,
    ClassificationResult,
)
from config import CONFIG
from version import __version__
from streamlit_helpers import compute_stats

logger = get_logger(__name__)


def _log_message(msg: str, placeholder: Optional[st.delta_generator.DeltaGenerator] = None) -> None:
    """Append a message to the session log and optionally refresh the UI."""
    logger.info(msg)
    st.session_state.setdefault("logs", [])
    st.session_state["logs"].append(msg)
    if placeholder is not None:
        placeholder.write("\n".join(st.session_state["logs"]))


def _pick_directory() -> Optional[str]:
    """Return a selected folder path or ``None`` when unavailable."""
    try:
        from tkinter import Tk, filedialog
    except Exception as exc:  # pragma: no cover - import may fail on headless systems
        logger.warning("Tkinter unavailable: %s", exc)
        st.warning("Folder picker unavailable. Please type the path manually.")
        return None

    try:
        root = Tk()
        root.withdraw()
        path = filedialog.askdirectory()
        root.destroy()
        return path or None
    except Exception as exc:  # pragma: no cover - UI feedback only
        logger.warning("Folder picker failed: %s", exc)
        st.warning("Folder picker unavailable. Please type the path manually.")
        return None


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
    _log_message(
        f"{result.file_name}: {result.model_determination} ({result.status})"
    )


def _update_table(placeholder: st.delta_generator.DeltaGenerator) -> None:
    """Render results in the given placeholder."""
    df = pd.DataFrame(st.session_state.get("results", []))
    if df.empty:
        placeholder.empty()
        return
    placeholder.dataframe(df, use_container_width=True)
    st.session_state["stats"] = compute_stats(st.session_state["results"])



def _run_folder(
    path: Path,
    engine: ClassificationEngine,
    mode: str,
    years: int | None,
    max_lines: int,
    table_ph: st.delta_generator.DeltaGenerator,
) -> None:
    """Classify every supported file in ``path`` recursively."""
    if not path.exists() or not path.is_dir():
        st.error("Folder does not exist")
        return

    scanner = FileScanner()
    file_paths = [
        info.path
        for info in scanner.scan_directory(path)
        if info.category != "skip"
    ]
    progress = st.progress(0)
    log_ph = st.session_state.get("log_placeholder")
    for idx, p in enumerate(file_paths, start=1):
        _log_message(f"Processing {p.name}", log_ph)
        with st.spinner(f"Processing {p.name}"):
            try:
                res = engine.classify_file(
                    p,
                    run_mode=mode,
                    threshold_years=years or 6,
                    max_lines=max_lines,
                )
            except Exception as exc:  # pragma: no cover - UI feedback only
                logger.exception("Classification failed")
                st.error(f"Failed to classify {p.name}: {exc}")
                _log_message(f"Failed {p.name}: {exc}", log_ph)
                continue
        _append_result(res)
        _update_table(table_ph)
        progress.progress(idx / len(file_paths))
        _log_message(f"Finished {p.name}", log_ph)
    progress.empty()


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
    st.sidebar.markdown(
        "<p style='text-align:center'>"
        "<img src='PC_Logo_Round_white.png' width='80'/></p>",
        unsafe_allow_html=True,
    )
    st.sidebar.title("Pierce County Records Classifier")
    st.sidebar.write(f"Version {__version__}")

    engine = get_engine()

    mode = st.sidebar.radio(
        "Mode",
        options=["Classification", "Last Modified"],
        help="Choose 'Classification' to analyze a document or 'Last Modified' to auto-destroy old files.",
    )

    max_lines = st.sidebar.slider(
        "Lines per file",
        10,
        500,
        CONFIG.max_lines,
        help="Limit text passed to the model",
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
    table_ph = st.empty()
    with st.sidebar.expander("Activity Log", expanded=True):
        log_ph = st.empty()
    st.session_state["log_placeholder"] = log_ph

    folder = st.text_input("Folder to scan", key="folder_path")
    if st.button("Browse", key="browse_btn"):
        chosen = _pick_directory()
        if chosen:
            st.session_state.folder_path = chosen
    if folder and st.button("Scan Folder", key="scan_btn"):
        _run_folder(Path(folder), engine, mode, years, max_lines, table_ph)

    _update_table(table_ph)
    _show_stats()


if __name__ == "__main__":
    main()
