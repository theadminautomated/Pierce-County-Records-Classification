"""
README.md - Pierce County Electronic Records Classifier (Root)

# Pierce County Electronic Records Classifier (Root)

## Overview
This repository provides a modern, production-ready toolkit for electronic records classification using a custom LLM (Ollama) and a user-friendly GUI/CLI. All analysis is performed locally for privacy and compliance.

## Repository Structure
- `Electronic-Records-Classification.py`: Production CLI for records classification
- `RecordsClassifierGui/`: Modern GUI for records classification
- `pierce-county-records-classifier-phi2/`: Custom LLM model for Ollama
- `Deploy.ps1`: Automated deployment and model import
- `Modelfile`: LLM prompt and configuration

## Deployment Steps
1. Install Python 3.8+ and Ollama
2. Run `Deploy.ps1` to import the model
3. Use the CLI or GUI as needed

## Production-Ready Features
- All core logic, validation, and UI flows are implemented and robust
- All visible actions are implemented or clearly marked as "Coming Soon" (bulk move/delete)
- Accessibility: color contrast, font size, keyboard navigation, and tooltips for all controls
- Real-time feedback, micro-animations, and status indicators
- Version number is shown in the window title
- All documentation and help text are up-to-date

## How It Works
- In the GUI, click the "How It Works" button for a summary of the workflow
- The app scans files, extracts and cleans content, applies 6-year retention, classifies with LLM, validates output, and updates the table in real time
- You can select files and export results to CSV
- Bulk move/delete are planned for a future release and are disabled in the UI

## Advanced Usage
- **CLI Mode**: Use `Electronic-Records-Classification.py` for batch/automated jobs
- **Custom Model**: Swap out the model in `Deploy.ps1` for new LLMs
- **Settings Reset**: Delete `.pc_records_classifier_settings.pkl` in your home directory

## Troubleshooting
- **PowerShell execution policy**: The script uses `-ExecutionPolicy Bypass` where needed
- **Missing dependencies**: The app checks and prompts for all required packages
- **Ollama/model not found**: Run `Deploy.ps1` or contact IT
- **File permission errors**: Ensure you have read/write access to all folders
- **GUI not launching**: Check Python and dependency versions
- **Import errors**: Ensure you launch the app using `run_app.py` or the VS Code task, not directly via `RecordsClassifierGui.py`

## FAQ
**Q: Is any data sent to the cloud?**
A: No. All analysis is local and private.

**Q: Can I use this on Mac/Linux?**
A: The GUI is Windows-optimized, but CLI may work cross-platform.

**Q: How do I update the LLM model?**
A: Replace the model in `Deploy.ps1` and rerun the script.

**Q: Where are settings stored?**
A: In your home directory as `.pc_records_classifier_settings.pkl`.

## Developer Notes
- All major functions and UI elements are documented with docstrings
- Modular codebase: UI, logic, and validation are separated
- Use the TODO list above to guide contributions
- See inline comments for advanced customization

---

*Validated as of 2025-05-29: This application is production and market ready. All dependencies, model checks, and packaging steps are automated and robust. Bulk move/delete are planned for a future release.*

Pierce County IT | 2025
"""