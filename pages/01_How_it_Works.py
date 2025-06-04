"""Streamlit page explaining how the Records Classifier works."""
import streamlit as st


def main() -> None:
    """Render the How It Works page."""
    st.title("How It Works")

    st.markdown(
        """
        ### Overview
        The Records Classifier helps determine whether a document should be
        **kept**, **destroyed**, or is **transitory**. Everything runs locally on
        your computer for maximum privacy.
        """
    )

    st.markdown(
        """
        ### Step by Step
        1. **Upload a file** using the *Browse* button on the main page.
        2. The app first checks the file's **last modified date**. If it is
           older than **6 years** (or the number of years you chose), the file
           is immediately marked **DESTROY** without further analysis.
        3. If the file is newer, the app reads a small portion of the text
           (about 100 lines) directly from the document.
        4. A lightweight language model then looks for important keywords from
           Washington State's Schedule 6 retention guidelines. These words give
           clues about whether something is an official record, a financial
           document, personnel information, or just a temporary note.
        5. The model adds up these clues to calculate a **confidence score** and
           picks one of three labels: **KEEP**, **DESTROY**, or **TRANSITORY**.
        6. The result and a short explanation appear on screen so you know why
           the decision was made.
        """
    )

    st.markdown(
        """
        ### Key Points
        - **No internet connection is required.** The model and keyword lists are
          built in, so your files never leave your machine.
        - **Confidence scores** come from counting how many keywords match your
          text. More matches mean higher confidence.
        - The **context snippet** shown with the result is just a small piece of
          your document that triggered the match. It helps you see why the file
          was classified a certain way.
        - When no keywords are found, the app defaults to **TRANSITORY** because
          there is not enough evidence that the file is important.
        """
    )

    st.info(
        "If you are ever unsure about a decision, please consult your records "
        "manager for guidance."
    )


if __name__ == "__main__":  # pragma: no cover - manual execution only
    main()
