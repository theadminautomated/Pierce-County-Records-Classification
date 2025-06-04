"""Streamlit interface for the Pierce County Records Classifier."""
import io
import logging
from pathlib import Path

import streamlit as st
from RecordsClassifierGui.logic.classification_engine_fixed import ClassificationEngine
from config import CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_file_content(uploaded_file) -> str:
    """Read uploaded file into a temporary path and return the path."""
    data = uploaded_file.read()
    temp_path = Path(st.session_state.get("temp_dir", "./tmp"))
    temp_path.mkdir(exist_ok=True)
    file_path = temp_path / uploaded_file.name
    file_path.write_bytes(data)
    return str(file_path)


def main() -> None:
    """Run the Streamlit UI."""
    st.set_page_config(page_title="Records Classifier", page_icon="📄", layout="wide")
    st.title("Pierce County Electronic Records Classifier")
    st.write("Model: %s" % CONFIG.model_name)

    engine = ClassificationEngine()

    uploaded_file = st.file_uploader("Upload a file for classification")
    if uploaded_file:
        file_path = load_file_content(uploaded_file)
        with st.spinner("Classifying..."):
            result = engine.classify_file(file_path)
        st.success("Classification complete")
        st.json({
            "file": result.file_name,
            "determination": result.model_determination,
            "confidence": result.confidence_score,
            "insights": result.contextual_insights,
        })


if __name__ == "__main__":
    main()
