# config_util.py
import json
import os
from pathlib import Path
import logging
from typing import Optional

CONFIG_FILE = "config.json"
logger = logging.getLogger(__name__)

# Get the backend directory path
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))

def validate_directory(path: str) -> tuple[bool, str]:
    """
    Validate if a directory path is usable for saving files.
    Returns (is_valid, error_message).
    """
    try:
        path = os.path.expanduser(path)  # Expand ~ to user home directory
        
        # If path is not absolute, make it relative to backend directory
        if not os.path.isabs(path):
            path = os.path.join(BACKEND_DIR, path)
        
        path = os.path.abspath(path)     # Convert to absolute path
        
        # Check if path exists or can be created
        os.makedirs(path, exist_ok=True)
        
        # Check if directory is writable
        test_file = Path(path) / '.write_test'
        try:
            test_file.touch()
            test_file.unlink()
        except Exception as e:
            return False, f"Directory is not writable: {str(e)}"
        
        return True, ""
    except Exception as e:
        return False, str(e)

def load_config() -> dict:
    """Load configuration from JSON file"""
    config_path = os.path.join(BACKEND_DIR, CONFIG_FILE)
    try:
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading config: {e}")
    return {}

def save_config(config: dict) -> None:
    """Save configuration to JSON file"""
    config_path = os.path.join(BACKEND_DIR, CONFIG_FILE)
    try:
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving config: {e}")
        raise

def get_output_directory() -> str:
    """
    Get the configured output directory.
    Falls back to default if not configured or invalid.
    """
    config = load_config()
    path = config.get("output_directory")
    
    if path:
        is_valid, _ = validate_directory(path)
        if is_valid:
            return os.path.abspath(path)
    
    # Fallback to default
    default_path = os.path.join(BACKEND_DIR, "output")
    os.makedirs(default_path, exist_ok=True)
    return default_path

def set_output_directory_config(new_path: str) -> str:
    """
    Set and validate new output directory.
    Returns the normalized absolute path if successful.
    Raises ValueError if directory is invalid.
    """
    is_valid, error = validate_directory(new_path)
    if not is_valid:
        raise ValueError(f"Invalid directory: {error}")
    
    # If path is relative, make it relative to backend directory
    if not os.path.isabs(new_path):
        new_path = os.path.join(BACKEND_DIR, new_path)
    
    abs_path = os.path.abspath(new_path)
    config = load_config()
    config["output_directory"] = abs_path
    save_config(config)
    
    return abs_path