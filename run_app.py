#!/usr/bin/env python
"""
Enhanced launcher for Records Classifier that ensures the correct working directory
and checks for required dependencies.

Author: Pierce County IT
Date: 2025-05-28
"""

import os
import sys
from pathlib import Path
import subprocess
import time
import socket
import platform
import shutil
import asyncio

def ensure_ollama_running():
    """Ensure Ollama is running locally and start it if not."""
    import subprocess
    import platform
    import socket
    import os
    import time
    import shutil
    from pathlib import Path

    OLLAMA_PORT = 11434
    OLLAMA_HOST = "localhost"
    MODEL_NAME = "pierce-county-records-classifier-phi2:latest"

    # Get the directory where the EXE/script is located
    if getattr(sys, 'frozen', False):
        # Running as EXE
        base_dir = Path(sys.executable).parent
    else:
        # Running as script
        base_dir = Path(__file__).parent

    # Set up model directories
    user_home = Path.home()
    ollama_dir = user_home / ".ollama"
    models_dir = ollama_dir / "models"
    manifests_dir = models_dir / "manifests"
    blobs_dir = models_dir / "blobs"

    # Create directories if they don't exist
    for d in [ollama_dir, models_dir, manifests_dir, blobs_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # Copy model files from our bundled directory to Ollama directory
    bundled_models = base_dir / "models"
    if bundled_models.exists():
        print("Copying bundled model files...")
        # Copy manifests
        for f in (bundled_models / "manifests").glob("*"):
            target = manifests_dir / f.name
            if not target.exists():
                shutil.copy2(f, target)
                print(f"Copied manifest: {f.name}")
        # Copy blobs
        for f in (bundled_models / "blobs").glob("*"):
            target = blobs_dir / f.name
            if not target.exists():
                shutil.copy2(f, target)
                print(f"Copied blob: {f.name}")

    # Copy Modelfile if it exists
    modelfile_src = bundled_models / "Modelfile-phi2"
    if modelfile_src.exists():
        modelfile_dest = models_dir / "Modelfile-phi2"
        if not modelfile_dest.exists():
            shutil.copy2(modelfile_src, modelfile_dest)
            print("Copied Modelfile")

    # Set up OLLAMA_MODELS env var
    os.environ["OLLAMA_MODELS"] = str(models_dir)

    # Always use user profile for shipped binary
    ollama_exe = user_home / "ollama.exe"

    # Copy Ollama binary if needed
    if not ollama_exe.exists():
        bundled_ollama = base_dir / "ollama.exe"
        if bundled_ollama.exists():
            shutil.copy2(bundled_ollama, ollama_exe)
            print("Copied Ollama binary")

    # Check if service is running
    print("Checking Ollama service...")
    try:
        with socket.create_connection((OLLAMA_HOST, OLLAMA_PORT), timeout=1.0):
            print("Ollama service is running")
            return True
    except (socket.timeout, ConnectionRefusedError):
        pass

    print("Starting Ollama service...")
    # Start the service
    if platform.system() == "Windows":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        subprocess.Popen([str(ollama_exe), "serve"], startupinfo=startupinfo)
    else:
        subprocess.Popen(["ollama", "serve"])

    # Wait for service to start with timeout
    start_time = time.time()
    while time.time() - start_time < 30:  # 30 second timeout
        try:
            with socket.create_connection((OLLAMA_HOST, OLLAMA_PORT), timeout=1.0):
                print("Ollama service started successfully")
                return True
        except (socket.timeout, ConnectionRefusedError):
            time.sleep(1)

    print("Failed to start Ollama service")
    return False

def main():
    """Main entry point for the application launcher"""
    ensure_ollama_running()
    # Get the directory where this script is located
    script_dir = Path(__file__).resolve().parent
    
    # Add the project root to Python path
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))
      # Add the RecordsClassifierGui package directory to Python path
    package_dir = script_dir / 'RecordsClassifierGui'
    if str(package_dir) not in sys.path:
        sys.path.insert(0, str(package_dir))
    
    try:
        from RecordsClassifierGui.gui.app import RecordsClassifierApp
        app = RecordsClassifierApp()
        
        # Start Tkinter mainloop
        app.mainloop()

        # After mainloop exits, close the asyncio loop properly
        print("Application closing. Finalizing asyncio tasks...")
        if hasattr(app, 'async_loop') and app.async_loop.is_running():
            # Give pending tasks a chance to complete or be cancelled
            # Gather all tasks
            tasks = [task for task in asyncio.all_tasks(loop=app.async_loop) if not task.done()]
            if tasks:
                print(f"Cancelling {len(tasks)} outstanding asyncio tasks...")
                for task in tasks:
                    task.cancel()
                # Wait for tasks to be cancelled
                app.async_loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
            
            print("Stopping asyncio event loop...")
            # The loop should be stopped by its own mechanism if _update_asyncio is no longer called
            # However, explicit cleanup is good.
            # app.async_loop.call_soon_threadsafe(app.async_loop.stop) # This might not be needed if _update_asyncio stops
            
            # Ensure the loop is fully stopped and async generators are shut down
            if not app.async_loop.is_closed():
                app.async_loop.run_until_complete(app.async_loop.shutdown_asyncgens())
                app.async_loop.close()
            print("Asyncio event loop closed.")
        elif hasattr(app, 'async_loop') and not app.async_loop.is_closed():
            # If the loop isn't running but isn't closed, try to close it.
            print("Asyncio loop was not running but is not closed. Attempting cleanup...")
            app.async_loop.run_until_complete(app.async_loop.shutdown_asyncgens())
            app.async_loop.close()
            print("Asyncio event loop closed.")
        else:
            print("No active/unclosed asyncio loop found on app instance.")

    except ImportError as e:
        print(f"Error importing RecordsClassifierApp: {e}")
        print(f"Python path: {sys.path}")
        sys.exit(1)

if __name__ == "__main__":
    main()
