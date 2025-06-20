# Pierce County Electronic Records Classifier

The Records Classifier sorts documents into **Keep**, **Destroy**, or **Transitory** categories using a small language model that runs entirely on your computer. Nothing leaves your machine and the app works offline for maximum privacy.

![New UI](docs/ui_after.png)
![Old UI](docs/ui_before.png)

## Purpose
- Automate retention decisions based on the county schedule
- Provide a safe, easy‑to‑use interface for all staff
- Give IT admins simple ways to update models and dependencies

## Main Features
1. Modern Streamlit web interface
2. Local classification engine with lightweight heuristics
3. Works with PDF, Office, images, and text files
4. Export results to CSV
5. Adjustable lines-per-file slider to control context size
6. Responsive layout with dark mode and keyboard navigation
7. **Last Modified mode** with a slider shown only when this mode is selected
8. Inline rerun (↻) and export (⬇) buttons appear after a job completes
9. Extensive Schedule 6 keyword list for accurate classification
10. Clear results table showing **File Path** and a new **NA** category for skipped files
11. Dedicated **How It Works** page with a plain‑language walkthrough
12. Live results table with real-time progress and summary stats
13. Sidebar folder picker with county logo branding

## System Requirements
- Windows 10/11 or macOS/Linux with Python **3.8+**
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- `antiword` for legacy `.doc` files (Windows only)
- Optional: Docker for container deployments

## Quick Start (One‑Click EXE)
1. Double‑click the installer provided by IT
2. Launch **Records Classifier** from the Start Menu
3. Upload a file and wait for the results

## Manual Setup
1. Install Python 3.8+
2. `pip install -r requirements.txt`
3. Optionally edit `config.yaml` to customize the model or Ollama URL
   (`PCRC_HF_CACHE` can override the Hugging Face cache directory)
4. Ensure Tesseract and (on Windows) antiword are on your `PATH`
5. Run `Deploy.ps1` once to load the model
6. Start the UI with `streamlit run app.py`
   (or run `python run_app.py` if Streamlit isn't on your PATH)
7. Optional: `python run_local.py --model <name>` to launch the local LLM API

### Windows Build Helper
If `cargo check` fails on Windows because the MSVC environment isn't loaded,
run `scripts/setup_windows_env.ps1` in a PowerShell prompt before building.
The script uses `vswhere` to locate Visual Studio Build Tools and sets the
required variables for the current session.

### Running the Local LLM
`run_local.py` downloads models to `models/` and serves a simple `/generate`
endpoint using FastAPI and Uvicorn. Use `--quant 4` or `--quant 8` for
quantized loading and `--port` to choose the port.

## Minimal Path to Awesome (Users)
1. Open the app
2. Click **Browse** and choose a document
3. Watch the spinner and progress messages
4. Read the decision and confidence score
5. Switch to **Last Modified** mode and adjust the slider to list files older than your chosen number of years
6. Enter a folder path in the sidebar and click **Scan Folder** to process files recursively
7. When finished, use the ↻ button to analyze again or the ⬇ button to save results

## Minimal Path to Awesome (IT Admins)
1. Review `config.yaml` or set environment variables for model location
2. Place updated model files in `pierce-county-records-classifier-phi2/`
3. Install Tesseract and antiword on target machines
4. Run `build_installer.ps1` to create a signed installer
5. Distribute the installer to users

## Troubleshooting
- **Missing model**: run `Deploy.ps1` again or contact IT
- **OCR errors**: verify Tesseract is installed and on `PATH`
- **App will not start**: reinstall using the latest installer
- **Folder picker unavailable**: type the folder path manually in the sidebar

## Building an Installer
1. Install Inno Setup and PyInstaller
2. Run `build_installer.ps1`
3. The signed installer appears in `release/`

## Updating Models & Binaries
- Place new model files in `pierce-county-records-classifier-phi2/`
- Update `config.yaml` or environment variables if using a different model
- Ensure Tesseract and antiword executables are included on target machines

## UI Modernization
Screenshots of the classic interface and the new Streamlit UI are in `docs/`.
Key improvements:
- Responsive design works on tablets and desktops
- Clear color contrast and keyboard shortcuts
- Progress spinners and status messages for every step

The classifier labels files as **KEEP**, **DESTROY**, **TRANSITORY**, or **NA**. "NA" is used for files that are skipped because they are unreadable or an unsupported type. Anything older than 6 years is automatically marked **DESTROY** and bypasses the LLM entirely, with contextual insights set to "Older than 6 years - automatic destroy".

## About
Version: `1.2.0`
Support: [records-support@example.com](mailto:records-support@example.com)
