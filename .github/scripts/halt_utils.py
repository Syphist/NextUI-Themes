#!/usr/bin/env python3
"""
Utilities for handling the halt.json marker file
"""

import os
import json
from pathlib import Path

# Base paths
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
UPLOADS_DIR = REPO_ROOT / "Uploads"
THEMES_HALT_PATH = UPLOADS_DIR / "Themes" / "halt.json"
COMPONENTS_HALT_PATH = UPLOADS_DIR / "Components" / "halt.json"

def get_halt_file_path(is_theme=True):
    """Get the path to the appropriate halt.json file"""
    return THEMES_HALT_PATH if is_theme else COMPONENTS_HALT_PATH

def load_halt_file(is_theme=True):
    """Load the halt.json file if it exists"""
    halt_path = get_halt_file_path(is_theme)

    if os.path.exists(halt_path):
        try:
            with open(halt_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Invalid halt.json, creating a new one")
        except Exception as e:
            print(f"Error reading halt file: {str(e)}")

    # Return default structure if file doesn't exist or has errors
    return {"halted": []}

def save_halt_file(halt_data, is_theme=True):
    """Save the halt.json file"""
    halt_path = get_halt_file_path(is_theme)

    # Ensure directory exists
    os.makedirs(os.path.dirname(halt_path), exist_ok=True)

    with open(halt_path, 'w') as f:
        json.dump(halt_data, f, indent=2)
    print(f"Updated halt file saved to {halt_path}")

def add_to_halt_file(item_name, is_theme=True):
    """Add an item to the halt file"""
    halt_data = load_halt_file(is_theme)

    if item_name not in halt_data["halted"]:
        halt_data["halted"].append(item_name)
        save_halt_file(halt_data, is_theme)
        print(f"Added {item_name} to halt file")
    else:
        print(f"{item_name} already in halt file")

def remove_from_halt_file(item_name, is_theme=True):
    """Remove an item from the halt file"""
    halt_data = load_halt_file(is_theme)

    if item_name in halt_data["halted"]:
        halt_data["halted"].remove(item_name)
        save_halt_file(halt_data, is_theme)
        print(f"Removed {item_name} from halt file")
    else:
        print(f"{item_name} not in halt file")

def is_item_halted(item_name, is_theme=True):
    """Check if an item is in the halt file"""
    halt_data = load_halt_file(is_theme)
    return item_name in halt_data["halted"]