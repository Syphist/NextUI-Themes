#!/usr/bin/env python3
"""
Script to process the push.json file with theme and component submissions.
Updated to use the .metadata folder structure for previews and manifests.
"""

import os
import json
import shutil
import tempfile
import zipfile
import subprocess
import re
from pathlib import Path
from datetime import datetime

# Base paths
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
UPLOAD_DIR = REPO_ROOT / "Upload"
PACKAGES_DIR = REPO_ROOT / "Packages"
CATALOG_DIR = REPO_ROOT / "Catalog"
METADATA_DIR = CATALOG_DIR / ".metadata"
PUSH_JSON_PATH = UPLOAD_DIR / "push.json"

# Component types and their extensions
COMPONENT_TYPES = {
    "theme": ".theme",
    "wallpaper": ".bg",
    "icon": ".icon",
    "accent": ".acc",
    "led": ".led",
    "font": ".font",
    "overlay": ".over"
}

# Directory name mappings for catalog (capitalized)
CATALOG_DIR_MAPPINGS = {
    "theme": "Themes",
    "wallpaper": "Wallpapers",
    "icon": "Icons",
    "accent": "Accents",
    "led": "LEDs",
    "font": "Fonts",
    "overlay": "Overlays"
}

def load_push_json():
    """Load the push.json file"""
    if not PUSH_JSON_PATH.exists():
        print(f"Error: {PUSH_JSON_PATH} does not exist")
        return None

    try:
        with open(PUSH_JSON_PATH, 'r') as f:
            push_data = json.load(f)
        return push_data
    except json.JSONDecodeError as e:
        print(f"Error parsing push.json: {e}")
        return None
    except Exception as e:
        print(f"Error loading push.json: {e}")
        return None

def validate_submission(submission):
    """Validate a submission entry"""
    # Basic required fields for all submissions
    required_fields = ["type", "name", "author", "submission_method"]

    # Check for required fields
    for field in required_fields:
        if field not in submission:
            print(f"Error: Missing required field '{field}' in submission")
            return False

    # Validate type
    if submission["type"] not in COMPONENT_TYPES:
        print(f"Error: Invalid type '{submission['type']}'. Must be one of: {', '.join(COMPONENT_TYPES.keys())}")
        return False

    # Validate name
    if not submission["name"].endswith(COMPONENT_TYPES[submission["type"]]):
        print(f"Error: Name '{submission['name']}' must end with '{COMPONENT_TYPES[submission['type']]}'")
        return False

    # Validate submission_method
    if submission["submission_method"] not in ["repository", "zip"]:
        print(f"Error: Invalid submission_method '{submission['submission_method']}'. Must be 'repository' or 'zip'")
        return False

    # Validate repository-specific fields only if submission method is "repository"
    if submission["submission_method"] == "repository":
        # Check for required repository fields
        repo_fields = ["repository_url", "commit"]
        for field in repo_fields:
            if field not in submission or not submission[field] or submission[field] == "None":
                print(f"Error: '{field}' is required for repository submissions")
                return False

        # Branch is optional, but if provided should not be "None"
        if "branch" not in submission:
            submission["branch"] = "main"  # Default to main if not specified

    # Check for zip file if submission_method is zip
    if submission["submission_method"] == "zip":
        zip_path = UPLOAD_DIR / f"{submission['name']}.zip"
        if not zip_path.exists():
            print(f"Error: Zip file '{zip_path}' not found for zip submission")
            return False

    return True

def clean_existing_entry(submission):
    """Clean up existing entry with the same name from catalog and packages"""
    name = submission["name"]
    component_type = submission["type"]

    # Load catalog.json
    catalog_path = CATALOG_DIR / "catalog.json"
    if not catalog_path.exists():
        print(f"Note: No catalog.json found, skipping cleanup")
        return

    try:
        with open(catalog_path, 'r') as f:
            catalog = json.load(f)

        # Check if entry exists in catalog
        entry_exists = False
        if component_type == "theme":
            if name in catalog.get("themes", {}):
                entry_exists = True
                entry_info = catalog["themes"][name]
        else:
            comp_type_key = COMPONENT_TYPES[component_type][1:]  # Remove the dot
            if comp_type_key in catalog.get("components", {}) and name in catalog["components"][comp_type_key]:
                entry_exists = True
                entry_info = catalog["components"][comp_type_key][name]

        if entry_exists:
            print(f"Found existing entry for {name}, cleaning up...")

            # Remove preview file from .metadata
            if "preview_path" in entry_info:
                preview_path = REPO_ROOT / entry_info["preview_path"]
                if preview_path.exists():
                    os.remove(preview_path)
                    print(f"Removed {preview_path}")

            # Remove manifest file from .metadata
            if "manifest_path" in entry_info:
                manifest_path = REPO_ROOT / entry_info["manifest_path"]
                if manifest_path.exists():
                    os.remove(manifest_path)
                    print(f"Removed {manifest_path}")

            # Remove package file
            if "URL" in entry_info:
                url = entry_info["URL"]
                # Extract the package path from the URL
                package_path_match = re.search(r'raw/main/(.+?)\.zip', url)
                if package_path_match:
                    package_rel_path = package_path_match.group(1) + ".zip"
                    package_path = REPO_ROOT / package_rel_path
                    if package_path.exists():
                        os.remove(package_path)
                        print(f"Removed {package_path}")

            # Remove extracted directory in Catalog
            if component_type == "theme":
                extracted_dir = CATALOG_DIR / "Themes" / name
            else:
                extracted_dir = CATALOG_DIR / CATALOG_DIR_MAPPINGS[component_type] / name

            if extracted_dir.exists() and extracted_dir.is_dir():
                shutil.rmtree(extracted_dir)
                print(f"Removed {extracted_dir}")

            print(f"Cleanup complete for {name}")
        else:
            print(f"No existing entry found for {name}, skipping cleanup")

    except Exception as e:
        print(f"Error during cleanup: {e}")

def clone_repository(repo_url, commit_hash, branch, target_dir):
    """Clone a repository at a specific commit and branch"""
    print(f"Cloning {repo_url} (branch: {branch}, commit: {commit_hash})")

    # Create target directory
    os.makedirs(os.path.dirname(target_dir), exist_ok=True)

    try:
        # Clone repository
        subprocess.run(['git', 'clone', '--no-checkout', repo_url, target_dir], check=True)

        # Change to repository directory
        cwd = os.getcwd()
        os.chdir(target_dir)

        try:
            # Fetch branch if specified
            if branch and branch != "None" and branch != "main":
                subprocess.run(['git', 'fetch', 'origin', branch], check=True)
                subprocess.run(['git', 'checkout', branch], check=True)
            else:
                subprocess.run(['git', 'checkout', 'main'], check=True)

            # Checkout specific commit
            subprocess.run(['git', 'checkout', commit_hash], check=True)

            # Remove .git directory
            shutil.rmtree('.git', ignore_errors=True)
        finally:
            # Return to original directory
            os.chdir(cwd)

        print(f"Repository cloned successfully at {target_dir}")
        return True
    except Exception as e:
        print(f"Error cloning repository: {e}")
        return False

def create_zip_file(source_dir, zip_path):
    """Create a ZIP file from a directory"""
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_name = os.path.relpath(file_path, source_dir)
                    zipf.write(file_path, arc_name)

        print(f"Created ZIP file: {zip_path}")
        return True
    except Exception as e:
        print(f"Error creating ZIP file: {e}")
        return False

def validate_package_contents(package_path):
    """Validate that the package zip file contains required files"""
    try:
        with zipfile.ZipFile(package_path, 'r') as zip_ref:
            file_list = zip_ref.namelist()

            # Check if manifest.json exists (at any level)
            manifest_exists = any('manifest.json' in f for f in file_list)

            # Check if preview.png exists (at any level)
            preview_exists = any('preview.png' in f for f in file_list)

            if not manifest_exists:
                print(f"Error: {package_path} is missing manifest.json")
                return False

            if not preview_exists:
                print(f"Error: {package_path} is missing preview.png")
                return False

            return True
    except Exception as e:
        print(f"Error validating package contents: {e}")
        return False

def extract_package(package_path, dest_dir):
    """Extract package without nested directories"""
    try:
        with zipfile.ZipFile(package_path, 'r') as zip_ref:
            file_list = zip_ref.namelist()

            # Identify if there's a common parent directory in the zip
            common_parent = None
            for item in file_list:
                # Skip __MACOSX entries
                if "__MACOSX" in item:
                    continue

                parts = item.split('/')
                if len(parts) > 1 and parts[0] and not common_parent:
                    common_parent = parts[0]
                elif len(parts) > 1 and parts[0] and parts[0] != common_parent:
                    common_parent = None
                    break

            # Don't strip the "Systems" directory for overlay components
            if common_parent == "Systems" and ".over" in str(package_path):
                common_parent = None

            # Extract files
            for item in file_list:
                # Skip __MACOSX entries
                if "__MACOSX" in item:
                    continue

                # Determine the correct extraction path
                if common_parent and item.startswith(common_parent + '/'):
                    # Strip the common parent directory
                    target_path = os.path.join(dest_dir, item[len(common_parent) + 1:])
                else:
                    target_path = os.path.join(dest_dir, item)

                # Skip directories
                if item.endswith('/'):
                    continue

                # Create the directory structure
                os.makedirs(os.path.dirname(target_path), exist_ok=True)

                # Extract the file
                with zip_ref.open(item) as source_file, open(target_path, 'wb') as target_file:
                    shutil.copyfileobj(source_file, target_file)

        # Remove any __MACOSX directory that might have been created
        macosx_dir = os.path.join(dest_dir, "__MACOSX")
        if os.path.exists(macosx_dir):
            shutil.rmtree(macosx_dir)

        print(f"Extracted package to {dest_dir}")
        return True
    except Exception as e:
        print(f"Error extracting package: {e}")
        return False

def copy_to_metadata(src_dir, component_type, name):
    """Copy preview.png and manifest.json to the .metadata directory"""
    try:
        # Get source files
        preview_src = os.path.join(src_dir, "preview.png")
        manifest_src = os.path.join(src_dir, "manifest.json")

        if not os.path.exists(preview_src):
            print(f"Error: preview.png not found in {src_dir}")
            return None, None

        if not os.path.exists(manifest_src):
            print(f"Error: manifest.json not found in {src_dir}")
            return None, None

        # Determine destination paths
        catalog_type_dir = CATALOG_DIR_MAPPINGS[component_type]

        preview_dest = METADATA_DIR / "previews" / f"{name}.png"
        manifest_dest = METADATA_DIR / "manifests" / f"{name}.json"

        # Create directories if they don't exist
        os.makedirs(os.path.dirname(preview_dest), exist_ok=True)
        os.makedirs(os.path.dirname(manifest_dest), exist_ok=True)

        # Copy files
        shutil.copy2(preview_src, preview_dest)
        shutil.copy2(manifest_src, manifest_dest)

        print(f"Copied preview and manifest to .metadata directory")

        # Return relative paths from REPO_ROOT
        preview_rel_path = str(preview_dest.relative_to(REPO_ROOT))
        manifest_rel_path = str(manifest_dest.relative_to(REPO_ROOT))

        return preview_rel_path, manifest_rel_path
    except Exception as e:
        print(f"Error copying to metadata: {e}")
        return None, None

def extract_metadata_from_manifest(manifest_path):
    """Extract author and description from manifest.json"""
    try:
        with open(manifest_path, 'r') as f:
            manifest_data = json.load(f)

        # Check if it's a theme or component
        if "theme_info" in manifest_data:
            author = manifest_data.get("theme_info", {}).get("author", "Unknown")
            description = manifest_data.get("theme_info", {}).get("name", os.path.basename(manifest_path).replace(".json", ""))
        else:
            author = manifest_data.get("component_info", {}).get("author", "Unknown")
            description = manifest_data.get("component_info", {}).get("name", os.path.basename(manifest_path).replace(".json", ""))

        # Extract systems for overlays
        systems = None
        if "content" in manifest_data and "systems" in manifest_data["content"]:
            systems = manifest_data["content"]["systems"]
            if isinstance(systems, list):
                systems.sort()

        return {
            "author": author,
            "description": description,
            "systems": systems
        }
    except Exception as e:
        print(f"Error extracting metadata from manifest: {e}")
        return {
            "author": "Unknown",
            "description": os.path.basename(manifest_path).replace(".json", ""),
            "systems": None
        }

def update_catalog(submission, preview_path, manifest_path, package_url):
    """Update catalog.json with the new entry"""
    catalog_path = CATALOG_DIR / "catalog.json"

    # Create catalog.json if it doesn't exist
    if not catalog_path.exists():
        initial_catalog = {
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "themes": {},
            "components": {
                "accents": {},
                "leds": {},
                "icons": {},
                "fonts": {},
                "wallpapers": {},
                "overlays": {}
            }
        }
        with open(catalog_path, 'w') as f:
            json.dump(initial_catalog, f, indent=2)

    # Load existing catalog
    try:
        with open(catalog_path, 'r') as f:
            catalog = json.load(f)
    except Exception as e:
        print(f"Error loading catalog: {e}")
        return False

    # Extract metadata from manifest (but use submission author as primary source)
    manifest_full_path = REPO_ROOT / manifest_path
    metadata = extract_metadata_from_manifest(manifest_full_path)

    # Create entry - Use author from submission (prioritize it over manifest)
    entry = {
        "preview_path": preview_path,
        "manifest_path": manifest_path,
        "author": submission["author"],  # Use author from submission
        "description": metadata["description"],
        "URL": package_url,
        "last_updated": datetime.utcnow().isoformat() + "Z"
    }

    # Add repository info if it's a repository submission
    if submission["submission_method"] == "repository":
        entry["repository"] = submission["repository_url"]
        entry["commit"] = submission["commit"]
        if "branch" in submission and submission["branch"] != "None":
            entry["branch"] = submission["branch"]
        else:
            entry["branch"] = "main"

    # Add systems for overlays
    if submission["type"] == "overlay" and metadata["systems"]:
        entry["systems"] = metadata["systems"]

    # Update catalog
    name = submission["name"]
    component_type = submission["type"]

    if component_type == "theme":
        # Add to themes section at the beginning
        themes = catalog.get("themes", {})

        # Create a new dictionary with the new entry first
        new_themes = {name: entry}

        # Add all other entries
        for theme_name, theme_info in themes.items():
            if theme_name != name:  # Skip the current one if it exists
                new_themes[theme_name] = theme_info

        catalog["themes"] = new_themes
    else:
        # Add to components section at the beginning
        comp_type_key = COMPONENT_TYPES[component_type][1:]  # Remove the dot
        components = catalog.get("components", {}).get(comp_type_key, {})

        # Create a new dictionary with the new entry first
        new_components = {name: entry}

        # Add all other entries
        for comp_name, comp_info in components.items():
            if comp_name != name:  # Skip the current one if it exists
                new_components[comp_name] = comp_info

        catalog["components"][comp_type_key] = new_components

    # Update last_updated timestamp
    catalog["last_updated"] = datetime.utcnow().isoformat() + "Z"

    # Save catalog
    try:
        with open(catalog_path, 'w') as f:
            json.dump(catalog, f, indent=2)
        print(f"Updated catalog.json with {name}")
        return True
    except Exception as e:
        print(f"Error saving catalog: {e}")
        return False

def process_repository_submission(submission):
    """Process a repository submission"""
    name = submission["name"]
    component_type = submission["type"]
    repo_url = submission["repository_url"]
    commit = submission["commit"]
    branch = submission["branch"]

    print(f"Processing repository submission: {name}")

    # Clean up existing entry
    clean_existing_entry(submission)

    # Create a temporary directory for cloning
    with tempfile.TemporaryDirectory() as temp_dir:
        # Clone repository
        if not clone_repository(repo_url, commit, branch, temp_dir):
            return False

        # Create a package file
        package_dir = PACKAGES_DIR / (component_type + "s")  # Add 's' to get themes, wallpapers, etc.
        os.makedirs(package_dir, exist_ok=True)

        package_path = package_dir / f"{name}.zip"
        if not create_zip_file(temp_dir, package_path):
            return False

        # Validate package contents
        if not validate_package_contents(package_path):
            return False

        # Extract package to Catalog
        catalog_type_dir = CATALOG_DIR_MAPPINGS[component_type]
        extract_dir = CATALOG_DIR / catalog_type_dir / name
        os.makedirs(extract_dir, exist_ok=True)

        if not extract_package(package_path, extract_dir):
            return False

        # Copy to .metadata directory
        preview_path, manifest_path = copy_to_metadata(extract_dir, component_type, name)
        if not preview_path or not manifest_path:
            return False

        # Generate package URL
        package_url = f"https://github.com/Leviathanium/NextUI-Themes/raw/main/Packages/{component_type}s/{name}.zip"

        # Update catalog
        if not update_catalog(submission, preview_path, manifest_path, package_url):
            return False

        print(f"Successfully processed repository submission: {name}")
        return True

def process_zip_submission(submission):
    """Process a zip submission"""
    name = submission["name"]
    component_type = submission["type"]

    print(f"Processing zip submission: {name}")

    # Clean up existing entry
    clean_existing_entry(submission)

    # Source zip file
    source_zip = UPLOAD_DIR / f"{name}.zip"

    # Validate package contents
    if not validate_package_contents(source_zip):
        return False

    # Copy to Packages directory
    package_dir = PACKAGES_DIR / (component_type + "s")  # Add 's' to get themes, wallpapers, etc.
    os.makedirs(package_dir, exist_ok=True)

    package_path = package_dir / f"{name}.zip"
    shutil.copy2(source_zip, package_path)
    print(f"Copied {source_zip} to {package_path}")

    # Extract package to Catalog
    catalog_type_dir = CATALOG_DIR_MAPPINGS[component_type]
    extract_dir = CATALOG_DIR / catalog_type_dir / name
    os.makedirs(extract_dir, exist_ok=True)

    if not extract_package(package_path, extract_dir):
        return False

    # Copy to .metadata directory
    preview_path, manifest_path = copy_to_metadata(extract_dir, component_type, name)
    if not preview_path or not manifest_path:
        return False

    # Generate package URL
    package_url = f"https://github.com/Leviathanium/NextUI-Themes/raw/main/Packages/{component_type}s/{name}.zip"

    # Update catalog
    if not update_catalog(submission, preview_path, manifest_path, package_url):
        return False

    print(f"Successfully processed zip submission: {name}")
    return True

def reset_push_json():
    """Reset push.json after successful processing"""
    empty_push = {
        "submission": []
    }

    try:
        with open(PUSH_JSON_PATH, 'w') as f:
            json.dump(empty_push, f, indent=2)
        print("Reset push.json to empty state")
        return True
    except Exception as e:
        print(f"Error resetting push.json: {e}")
        return False

def main():
    """Main function to process push.json"""
    print("Starting push.json processing")

    # Create necessary directories
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(PACKAGES_DIR, exist_ok=True)
    os.makedirs(CATALOG_DIR, exist_ok=True)
    os.makedirs(METADATA_DIR / "previews", exist_ok=True)
    os.makedirs(METADATA_DIR / "manifests", exist_ok=True)

    # Load push.json
    push_data = load_push_json()
    if not push_data:
        print("Failed to load push.json, aborting")
        return False

    # Check if push.json has submissions
    if "submission" not in push_data or not push_data["submission"]:
        print("No submissions found in push.json")
        return True

    # Process each submission
    success = True
    for submission in push_data["submission"]:
        # Validate submission
        if not validate_submission(submission):
            print(f"Validation failed for submission: {submission.get('name', 'unknown')}")
            success = False
            continue

        # Process submission based on method
        if submission["submission_method"] == "repository":
            if not process_repository_submission(submission):
                print(f"Failed to process repository submission: {submission['name']}")
                success = False
        elif submission["submission_method"] == "zip":
            if not process_zip_submission(submission):
                print(f"Failed to process zip submission: {submission['name']}")
                success = False

    # Reset push.json if all submissions were processed successfully
    if success:
        if not reset_push_json():
            print("Warning: Failed to reset push.json")
            success = False

    print("Push.json processing complete" if success else "Push.json processing completed with errors")
    return success

if __name__ == "__main__":
    success = main()
    if not success:
        # Exit with error code if there were any failures
        exit(1)