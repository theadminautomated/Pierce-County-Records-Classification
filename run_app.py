#!/usr/bin/env python
"""Records Classifier GUI Launcher – Production.

Loads and runs the main GUI app. LLM/model/service logic is invoked as needed by the app.
No dummy/test/stub code—this is the real deal.
"""

import logging
import sys
import os
from pathlib import Path
import importlib.util

def main():
    """Main entry point for the Records Classifier GUI app."""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Starting Records Classifier GUI...")

    # Add the project root to Python path
    script_dir = Path(__file__).resolve().parent
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))
    
    # Add the RecordsClassifierGui package directory to Python path
    package_dir = script_dir / "RecordsClassifierGui"
    if str(package_dir) not in sys.path:
        sys.path.insert(0, str(package_dir))
    
    # Set PYTHONPATH environment variable to help with relative imports
    current_pythonpath = os.environ.get('PYTHONPATH', '')
    new_paths = [str(script_dir), str(package_dir)]
    if current_pythonpath:
        os.environ['PYTHONPATH'] = os.pathsep.join(new_paths + [current_pythonpath])
    else:
        os.environ['PYTHONPATH'] = os.pathsep.join(new_paths)

    try:
        # Dynamically load the GUI application module (preserves package context)
        gui_app_path = package_dir / "gui" / "app.py"
        spec = importlib.util.spec_from_file_location(
            "RecordsClassifierGui.gui.app",
            str(gui_app_path),
            submodule_search_locations=[str(package_dir / "gui")]
        )
        app_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_module)
        RecordsClassifierApp = app_module.RecordsClassifierApp
        logger.info("Imported RecordsClassifierApp successfully.")

        # ---- Real production launch ----
        # Start Tkinter mainloop
        app = RecordsClassifierApp()
        app.mainloop()

        # After mainloop exits, close the asyncio loop properly
        logger.info("Application closing. Finalizing asyncio tasks...")
        import asyncio
        if hasattr(app, 'async_loop') and app.async_loop.is_running():
            tasks = [task for task in asyncio.all_tasks(loop=app.async_loop) if not task.done()]
            if tasks:
                logger.info("Cancelling %s outstanding asyncio tasks...", len(tasks))
                for task in tasks:
                    task.cancel()
                app.async_loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
            logger.info("Stopping asyncio event loop...")
            if not app.async_loop.is_closed():
                app.async_loop.run_until_complete(app.async_loop.shutdown_asyncgens())
                app.async_loop.close()
            logger.info("Asyncio event loop closed")
        elif hasattr(app, 'async_loop') and not app.async_loop.is_closed():
            logger.info("Asyncio loop was not running but is not closed. Attempting cleanup...")
            app.async_loop.run_until_complete(app.async_loop.shutdown_asyncgens())
            app.async_loop.close()
            logger.info("Asyncio event loop closed")
        else:
            logger.info("No active/unclosed asyncio loop found on app instance")
        # ---- End real launch ----

    except ImportError as e:
        logger.error("Error importing RecordsClassifierApp: %s", e)
        logger.error("Python path: %s", sys.path)
        logger.error("PYTHONPATH: %s", os.environ.get('PYTHONPATH', 'Not set'))
        
        # Try alternative import method
        try:
            logger.info("Attempting alternative import method...")
            # Fallback: import by full package path
            from RecordsClassifierGui.gui.app import RecordsClassifierApp
            logger.info("Alternative import successful.")
            
            app = RecordsClassifierApp()
            app.mainloop()
            
        except ImportError as e2:
            logger.error("Alternative import also failed: %s", e2)
            sys.exit(1)

    logger.info("App run complete.")

if __name__ == "__main__":
    main()