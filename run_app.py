#!/usr/bin/env python
"""Launch the Streamlit Records Classifier UI."""
import subprocess
import sys
import logging

logger = logging.getLogger(__name__)


def main() -> None:
    """Run ``app.py`` using the current Python interpreter."""
    logging.basicConfig(level=logging.INFO)
    try:
        subprocess.run([
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "app.py",
        ], check=True)
    except Exception as exc:
        logger.exception("Failed to launch Streamlit", exc_info=exc)


if __name__ == "__main__":
    main()
