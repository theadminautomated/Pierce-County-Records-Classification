#!/usr/bin/env python
"""
Dummy launcher for Records Classifier for code linting and UI logic refactor.

No Ollama/model/server calls. Can be safely run in headless and CI environments.

THE CODE BELOW IS THE ORIGINAL APP LAUNCH LOGIC — DO NOT FUCKING TOUCH.
"""

import sys
from pathlib import Path

def main():
    """Main entry point for the dummy app launcher."""
    print("Dummy app starting...")

    # Add the project root to Python path
    script_dir = Path(__file__).resolve().parent
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))

    # Add the RecordsClassifierGui package directory to Python path
    package_dir = script_dir / 'RecordsClassifierGui'
    if str(package_dir) not in sys.path:
        sys.path.insert(0, str(package_dir))

    try:
        from RecordsClassifierGui.gui.app import RecordsClassifierApp
        print("Imported RecordsClassifierApp successfully.")

        # ---- DO NOT FUCKING TOUCH: ORIGINAL LAUNCH CODE ----
        """
        # Start Tkinter mainloop
        app = RecordsClassifierApp()
        app.mainloop()

        # After mainloop exits, close the asyncio loop properly
        print("Application closing. Finalizing asyncio tasks...")
        if hasattr(app, 'async_loop') and app.async_loop.is_running():
            tasks = [task for task in asyncio.all_tasks(loop=app.async_loop) if not task.done()]
            if tasks:
                print(f"Cancelling {len(tasks)} outstanding asyncio tasks...")
                for task in tasks:
                    task.cancel()
                app.async_loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
            print("Stopping asyncio event loop...")
            if not app.async_loop.is_closed():
                app.async_loop.run_until_complete(app.async_loop.shutdown_asyncgens())
                app.async_loop.close()
            print("Asyncio event loop closed.")
        elif hasattr(app, 'async_loop') and not app.async_loop.is_closed():
            print("Asyncio loop was not running but is not closed. Attempting cleanup...")
            app.async_loop.run_until_complete(app.async_loop.shutdown_asyncgens())
            app.async_loop.close()
            print("Asyncio event loop closed.")
        else:
            print("No active/unclosed asyncio loop found on app instance.")
        """
        # ---- END DO NOT FUCKING TOUCH ----

        print("Skipping GUI launch in dummy run (headless/container safe).")
    except ImportError as e:
        print(f"Error importing RecordsClassifierApp: {e}")
        print(f"Python path: {sys.path}")
        sys.exit(1)

    print("Dummy app run complete.")

if __name__ == "__main__":
    main()
