#!/usr/bin/env python3
"""
Quick start script for PII Redaction API.
"""
import os
import sys
import subprocess


def check_python_version():
    """Check if Python version is 3.8 or higher."""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    return True


def check_env_file():
    """Check if .env file exists."""
    if not os.path.exists('.env'):
        print("Warning: .env file not found")
        print("Copying .env.example to .env...")
        try:
            with open('.env.example', 'r') as src:
                content = src.read()
            with open('.env', 'w') as dst:
                dst.write(content)
            print("✓ Created .env file")
            print("\n⚠️  IMPORTANT: Edit .env file with your Azure credentials before running!")
            return False
        except Exception as e:
            print(f"Error creating .env file: {e}")
            return False
    return True


def install_dependencies():
    """Install required Python packages."""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to install dependencies")
        return False


def run_app():
    """Run the Flask application."""
    print("\n" + "="*50)
    print("Starting PII Redaction API...")
    print("="*50)
    try:
        subprocess.call([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n\nShutting down...")


def main():
    """Main setup and run routine."""
    print("PII Redaction API - Quick Start")
    print("="*50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check for .env file
    env_ready = check_env_file()
    
    # Install dependencies
    print("\nChecking dependencies...")
    try:
        import flask
        import azure.ai.formrecognizer
        import azure.ai.textanalytics
        from PIL import Image
        print("✓ All dependencies are already installed")
    except ImportError:
        if not install_dependencies():
            sys.exit(1)
    
    # Final check
    if not env_ready:
        print("\n⚠️  Please edit the .env file with your Azure credentials")
        print("Then run: python app.py")
        sys.exit(0)
    
    # Run the application
    print("\n✓ Setup complete!")
    response = input("\nStart the API server? (y/n): ")
    if response.lower() == 'y':
        run_app()
    else:
        print("\nTo start the server later, run: python app.py")


if __name__ == "__main__":
    main()
