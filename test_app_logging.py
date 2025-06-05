import streamlit as st
from app import _log_message

def test_log_message():
    st.session_state.clear()
    placeholder = st.empty()
    _log_message("hi", placeholder)
    assert "hi" in st.session_state["logs"]
