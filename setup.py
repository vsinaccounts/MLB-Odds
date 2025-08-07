#!/usr/bin/env python3
"""
Setup script for MLB Odds Feed

This script helps set up the environment and validate the installation.
"""

import sys
import subprocess
import json
from datetime import datetime

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required.")
        return False
    print(f"✓ Python {sys.version.split()[0]} detected")
    return True

def install_requirements():
    """Install required packages."""
    try:
        print("Installing required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install requirements: {e}")
        return False

def test_imports():
    """Test if all required modules can be imported."""
    try:
        import requests
        import json
        from datetime import datetime, timezone
        print("✓ All required modules can be imported")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def run_test():
    """Run the test script to validate functionality."""
    try:
        print("Running test script...")
        subprocess.check_call([sys.executable, "test_feed.py"])
        print("✓ Test script completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Test script failed: {e}")
        return False
    except FileNotFoundError:
        print("✗ test_feed.py not found")
        return False

def create_example_config():
    """Create an example configuration file if needed."""
    try:
        import config
        print("✓ Configuration file found")
        return True
    except ImportError:
        print("Creating example configuration file...")
        example_config = '''"""
Configuration settings for the MLB Odds Feed
"""

# API Configuration
UNABATED_API_KEY = "your_api_key_here"

# API Endpoints (update these with actual Unabated API endpoints)
API_CONFIG = {
    'base_url': 'https://api.unabated.com',
    'endpoints': {
        'mlb_games': '/v1/sports/mlb/games',
        'mlb_odds': '/v1/sports/mlb/odds',
        'mlb_lines': '/v1/odds/mlb'
    },
    'timeout': 30,
    'max_retries': 3
}

# Other configuration...
'''
        with open('config_example.py', 'w') as f:
            f.write(example_config)
        print("✓ Example configuration created as config_example.py")
        return True

def main():
    """Main setup function."""
    print("MLB Odds Feed Setup")
    print("=" * 50)
    
    success = True
    
    # Check Python version
    if not check_python_version():
        success = False
    
    # Install requirements
    if success and not install_requirements():
        success = False
    
    # Test imports
    if success and not test_imports():
        success = False
    
    # Create example config if needed
    if success:
        create_example_config()
    
    # Run test
    if success and not run_test():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("✓ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Update config.py with your actual Unabated API key")
        print("2. Update API endpoints in config.py once you have the documentation")
        print("3. Run: python mlb_odds_feed.py")
    else:
        print("✗ Setup encountered errors. Please check the output above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())