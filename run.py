"""
Application runner script.
This script configures the system path and then starts the Uvicorn server.
Using this script ensures that the application's Python path is set correctly,
even when Uvicorn's reloader creates a new process.

To run the application:
python run.py
"""

import sys
import os
import uvicorn

def main():
    # Add the 'backend' directory to the Python path
    # This ensures that absolute imports like 'from app.core...' work correctly.
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend'))
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)

    # Change the current working directory to 'backend'
    # This is often necessary for relative paths inside the app (e.g., for templates or static files)
    # and helps Uvicorn find the application module.
    os.chdir(backend_dir)

    # Run the Uvicorn server
    # We specify the app as a string 'main:app'
    # 'reload_dirs' is set to the backend directory to watch for changes.
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[backend_dir],
        log_config=None, # We use structlog inside the app
    )

if __name__ == "__main__":
    main() 