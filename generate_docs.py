#!/usr/bin/env python
"""
Script to generate documentation for the auth module using pdoc.
"""
import os
import sys
import subprocess

def main():
    """Generate documentation for the auth module."""
    # Install pdoc if not already installed
    subprocess.run([sys.executable, "-m", "pip", "install", "pdoc"], check=True)
    
    # Create docs directory if it doesn't exist
    os.makedirs("docs", exist_ok=True)
    
    # Generate documentation for auth module
    subprocess.run([
        sys.executable, "-m", "pdoc", 
        "--output-dir", "docs", 
        "--html", 
        "--force",
        "src.flask_app.routes.auth"
    ], check=True)
    
    print("Documentation generated successfully in the docs directory")

if __name__ == "__main__":
    main()
