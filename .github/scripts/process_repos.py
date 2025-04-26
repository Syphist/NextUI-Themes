#!/usr/bin/env python3
"""
Script to process repository-based themes and components
"""

import os
import json
import shutil
import tempfile
import zipfile
import subprocess
from pathlib import Path
from datetime import datetime
from collections import OrderedDict
# Import the halt utilities
from halt_utils import add_to_halt_file, is_item_halted

# Base paths
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CATALOG_PATH = REPO_ROOT / "Catalog" / "catalog.json"
UPLOADS_THEMES_DIR = REPO_ROOT / "Uploads" / "Themes"
UPLOADS_COMPONENTS_DIR = REPO_ROOT / "Uploads" / "Components"
CATALOG_THEMES_DIR = REPO_ROOT / "Catalog" / "Themes"
CATALOG_COMPONENTS_DIR = REPO_ROOT / "Catalog" / "Components"

# Component type to directory mapping
COMPONENT_DIRS = {
    ".bg": "Wallpapers",
    ".icon": "Icons",
    ".acc": "Accents",
    ".led": "LEDs",
    ".font": "Fonts",
    ".over": "Overlays"
}

def load_catalog():
    """Load the catalog.json file with ordering preserved"""
    if not CATALOG_PATH.exists():
        print(f"Catalog file not found: {CATALOG_PATH}")
        return None

    try:
        with open(CATALOG_PATH, 'r') as f:
            catalog = json.load(f, object_pairs_hook=OrderedDict)
        return catalog
    except Exception as e:
        print(f"Error loading catalog: {e}")
        return None

def save_catalog(catalog):
    """Save the catalog.json file preserving order"""
    with open(CATALOG_PATH, 'w') as f:
        json.dump(catalog, f, indent=2)
    print(f"Updated catalog saved to {CATALOG_PATH}")

def clone_repository(repo_url, commit_hash, target_dir):
    """Clone a repository at a specific commit, with support for branch specifications"""
    # Parse the repository URL to handle branch specifications
    branch = None
    base_url = repo_url

    # Handle GitHub branch specifications in URL (e.g., /tree/Branch)
    if '/tree/' in repo_url:
        parts = repo_url.split('/tree/', 1)
        base_url = parts[0]
        branch = parts[1]
        print(f"Detected branch specification: {branch}")

    os.makedirs(os.path.dirname(target_dir), exist_ok=True)

    # Clone repository using the base URL (without branch specification)
    print(f"Cloning {base_url} at commit {commit_hash}")
    subprocess.run(['git', 'clone', '--no-checkout', base_url, target_dir], check=True)

    # Change to repository directory
    cwd = os.getcwd()
    os.chdir(target_dir)

    try:
        # If a branch was specified, fetch it explicitly before checkout
        if branch:
            print(f"Fetching branch: {branch}")
            subprocess.run(['git', 'fetch', 'origin', branch], check=True)

        # Checkout specific commit
        subprocess.run(['git', 'checkout', commit_hash], check=True)

        # Remove .git directory
        shutil.rmtree('.git', ignore_errors=True)
    finally:
        # Return to original directory
        os.chdir(cwd)

    print(f"Repository cloned successfully at {target_dir}")

def create_zip_file(source_dir, zip_path):
    """Create a ZIP file from a directory"""
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Calculate path relative to source_dir
                arc_name = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arc_name)

    print(f"Created ZIP file: {zip_path}")

def extract_preview_and_manifest(source_dir, name, is_theme=True):
    """Extract preview.png and manifest.json from a repository"""
    preview_path = os.path.join(source_dir, "preview.png")
    manifest_path = os.path.join(source_dir, "manifest.json")

    if not os.path.exists(preview_path):
        print(f"Warning: No preview.png found in {source_dir}")
        return None, None

    if not os.path.exists(manifest_path):
        print(f"Warning: No manifest.json found in {source_dir}")
        return None, None

    # Determine destination paths
    if is_theme:
        preview_dest = CATALOG_THEMES_DIR / "previews" / f"{name}.png"
        manifest_dest = CATALOG_THEMES_DIR / "manifests" / f"{name}.json"
    else:
        component_type = None
        for ext, dir_name in COMPONENT_DIRS.items():
            if name.endswith(ext):
                component_type = dir_name
                break

        if component_type is None:
            print(f"Warning: Could not determine component type for {name}")
            return None, None

        preview_dest = CATALOG_COMPONENTS_DIR / component_type / "previews" / f"{name}.png"
        manifest_dest = CATALOG_COMPONENTS_DIR / component_type / "manifests" / f"{name}.json"

    # Make sure destination directories exist
    os.makedirs(os.path.dirname(preview_dest), exist_ok=True)
    os.makedirs(os.path.dirname(manifest_dest), exist_ok=True)

    # Copy files
    shutil.copy2(preview_path, preview_dest)
    shutil.copy2(manifest_path, manifest_dest)

    return str(preview_dest.relative_to(REPO_ROOT)), str(manifest_dest.relative_to(REPO_ROOT))

def process_theme_repository(name, repo_url, commit_hash):
    """Process a theme repository and create a ZIP file"""
    print(f"Processing theme repository: {name} from {repo_url} at {commit_hash}")

    # Create a temporary directory for cloning
    with tempfile.TemporaryDirectory() as temp_dir:
        # Clone repository at specific commit
        clone_repository(repo_url, commit_hash, temp_dir)

        # Extract preview and manifest
        preview_path, manifest_path = extract_preview_and_manifest(temp_dir, name, is_theme=True)

        if preview_path is None or manifest_path is None:
            print(f"Warning: Could not extract preview or manifest for {name}")
            return None, None, None

        # Create uploads directory if it doesn't exist
        os.makedirs(UPLOADS_THEMES_DIR, exist_ok=True)

        # Create ZIP file
        zip_path = UPLOADS_THEMES_DIR / f"{name}.zip"
        create_zip_file(temp_dir, zip_path)

        # Add to halt file to prevent re-processing by process_zips.py
        add_to_halt_file(name, is_theme=True)

        # Generate URL for the ZIP file
        zip_url = f"https://github.com/Leviathanium/NextUI-Themes/raw/main/Uploads/Themes/{name}.zip"

        return preview_path, manifest_path, zip_url

def process_component_repository(name, repo_url, commit_hash):
    """Process a component repository and create a ZIP file"""
    print(f"Processing component repository: {name} from {repo_url} at {commit_hash}")

    # Determine component type
    component_type = None
    for ext, dir_name in COMPONENT_DIRS.items():
        if name.endswith(ext):
            component_type = dir_name
            break

    if component_type is None:
        print(f"Warning: Could not determine component type for {name}")
        # Return three values to avoid the "not enough values to unpack" error
        return None, None, None

    # Create a temporary directory for cloning
    with tempfile.TemporaryDirectory() as temp_dir:
        # Clone repository at specific commit
        clone_repository(repo_url, commit_hash, temp_dir)

        # Extract preview and manifest
        preview_path, manifest_path = extract_preview_and_manifest(temp_dir, name, is_theme=False)

        if preview_path is None or manifest_path is None:
            print(f"Warning: Could not extract preview or manifest for {name}")
            return None, None, None

        # Create uploads directory if it doesn't exist
        uploads_dir = UPLOADS_COMPONENTS_DIR / component_type
        os.makedirs(uploads_dir, exist_ok=True)

        # Create ZIP file
        zip_path = uploads_dir / f"{name}.zip"
        create_zip_file(temp_dir, zip_path)

        # Add to halt file to prevent re-processing by process_zips.py
        add_to_halt_file(name, is_theme=False)

        # Generate URL for the ZIP file
        zip_url = f"https://github.com/Leviathanium/NextUI-Themes/raw/main/Uploads/Components/{component_type}/{name}.zip"

        return preview_path, manifest_path, zip_url

def process_repository_entries():
    """Process all repository entries in the catalog that have pull_now=true"""
    catalog = load_catalog()
    if catalog is None:
        return

    # Process theme repositories
    updated = False
    for theme_name, theme_info in list(catalog.get("themes", {}).items()):
        # Check if this is a repository-based entry with pull_now=true
        if ("repository" in theme_info and
                "commit" in theme_info and
                theme_info.get("pull_now") == "true"):

            repo_url = theme_info["repository"]
            commit_hash = theme_info["commit"]

            # Process the repository
            preview_path, manifest_path, zip_url = process_theme_repository(
                theme_name, repo_url, commit_hash)

            if preview_path and manifest_path and zip_url:
                # Update catalog entry (preserve order by creating a new OrderedDict)
                new_info = OrderedDict()

                # Copy all existing fields except pull_now
                for key, value in theme_info.items():
                    if key != "pull_now":
                        new_info[key] = value

                # Add new fields
                new_info["preview_path"] = preview_path
                new_info["manifest_path"] = manifest_path
                if "description" not in new_info:
                    new_info["description"] = theme_name
                new_info["URL"] = zip_url

                # Add pull_now at the end and set to false
                new_info["pull_now"] = "false"

                # Replace the theme info in the catalog
                catalog["themes"][theme_name] = new_info

                updated = True
                print(f"Successfully processed theme: {theme_name} and set pull_now to false")
            else:
                print(f"Failed to process theme repository: {theme_name}")
                # Don't set pull_now to false if processing failed

    # Process component repositories
    for comp_type, components in catalog.get("components", {}).items():
        for comp_name, comp_info in list(components.items()):
            # Check if this is a repository-based entry with pull_now=true
            if ("repository" in comp_info and
                    "commit" in comp_info and
                    comp_info.get("pull_now") == "true"):

                repo_url = comp_info["repository"]
                commit_hash = comp_info["commit"]

                # Process the repository
                preview_path, manifest_path, zip_url = process_component_repository(
                    comp_name, repo_url, commit_hash)

                if preview_path and manifest_path and zip_url:
                    # Update catalog entry (preserve order by creating a new OrderedDict)
                    new_info = OrderedDict()

                    # Copy all existing fields except pull_now
                    for key, value in comp_info.items():
                        if key != "pull_now":
                            new_info[key] = value

                    # Add new fields
                    new_info["preview_path"] = preview_path
                    new_info["manifest_path"] = manifest_path
                    if "description" not in new_info:
                        new_info["description"] = comp_name
                    new_info["URL"] = zip_url

                    # Add pull_now at the end and set to false
                    new_info["pull_now"] = "false"

                    # Replace the component info in the catalog
                    catalog["components"][comp_type][comp_name] = new_info

                    updated = True
                    print(f"Successfully processed component: {comp_name} and set pull_now to false")
                else:
                    print(f"Failed to process component repository: {comp_name}")
                    # Don't set pull_now to false if processing failed

    # Update last_updated timestamp and save the catalog
    if updated:
        catalog["last_updated"] = datetime.utcnow().isoformat() + "Z"
        save_catalog(catalog)
        print("Catalog updated with pull_now flags set to false for processed items")

def main():
    """Main function"""
    print("Starting repository-based theme and component processing")
    process_repository_entries()
    print("Processing complete")

if __name__ == "__main__":
    main()