#!/usr/bin/env python3
"""
Script to build the NextUI-Themes catalog from extracted themes and components
"""

import os
import json
from datetime import datetime
from pathlib import Path
import traceback
from collections import OrderedDict

# Base paths
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CATALOG_DIR = REPO_ROOT / "Catalog"  # Changed from "catalog" to "Catalog"
THEMES_DIR = CATALOG_DIR / "Themes"  # Moved into Catalog
COMPONENTS_DIR = CATALOG_DIR / "Components"  # Moved into Catalog
UPLOADS_DIR = REPO_ROOT / "Uploads"  # Path to uploaded zips

# GitHub raw content base URL
GITHUB_RAW_URL = "https://github.com/Leviathanium/NextUI-Themes/raw/main/Uploads"

# Component types mapping
COMPONENT_TYPES = {
    "Accents": "accents",
    "LEDs": "leds",
    "Icons": "icons",
    "Fonts": "fonts",
    "Wallpapers": "wallpapers",
    "Overlays": "overlays"
}

def load_existing_catalog():
    """Load the existing catalog.json file if it exists, preserving order"""
    catalog_path = CATALOG_DIR / "catalog.json"
    if os.path.exists(catalog_path):
        try:
            with open(catalog_path, 'r') as f:
                return json.load(f, object_pairs_hook=OrderedDict)
        except json.JSONDecodeError:
            print(f"Warning: Existing catalog.json is invalid, creating a new one")
        except Exception as e:
            print(f"Error reading existing catalog: {str(e)}")

    # Return default structure if no catalog exists or there was an error
    return OrderedDict([
        ("last_updated", datetime.utcnow().isoformat() + "Z"),
        ("themes", OrderedDict()),
        ("components", OrderedDict([
            ("accents", OrderedDict()),
            ("leds", OrderedDict()),
            ("icons", OrderedDict()),
            ("fonts", OrderedDict()),
            ("wallpapers", OrderedDict()),
            ("overlays", OrderedDict())
        ]))
    ])

def merge_theme_info(theme_name, new_info, existing_info=None):
    """Merge new theme information with existing info, preserving metadata"""
    if existing_info is None:
        theme_info = OrderedDict()
    else:
        # Start with existing info to preserve all fields
        theme_info = OrderedDict(existing_info)

    # Update with new information
    for key, value in new_info.items():
        theme_info[key] = value

    # Always preserve repository metadata if it exists
    if "repository" in existing_info and "repository" not in new_info:
        theme_info["repository"] = existing_info["repository"]
    if "commit" in existing_info and "commit" not in new_info:
        theme_info["commit"] = existing_info["commit"]

    # If pull_now is set to true, DO NOT change it - let process_repos.py handle it
    # If pull_now is not present, don't add it (direct uploads)
    if "pull_now" in existing_info and existing_info["pull_now"] == "true":
        theme_info["pull_now"] = "true"

    return theme_info

def extract_theme_info(theme_path, existing_info=None):
    """Extract theme information from the theme directory and preview/manifest"""
    theme_name = os.path.basename(theme_path)

    # Start with minimal info to extract
    new_info = OrderedDict()
    if "INVALID" in new_info:
        del new_info["INVALID"]

    # Check for manifest in the theme directory
    theme_manifest_path = os.path.join(theme_path, "manifest.json")
    theme_preview_path = os.path.join(theme_path, "preview.png")

    # Check for manifest in the manifests directory
    manifests_dir_path = os.path.join(THEMES_DIR, "manifests", f"{theme_name}.json")

    # Check for preview in the previews directory
    previews_dir_path = os.path.join(THEMES_DIR, "previews", f"{theme_name}.png")

    # Determine which manifest to use
    if os.path.exists(theme_manifest_path):
        manifest_path = theme_manifest_path
    elif os.path.exists(manifests_dir_path):
        manifest_path = manifests_dir_path
    else:
        print(f"Warning: No manifest found for theme {theme_name}")
        new_info["INVALID"] = "No manifest.json file found"
        return merge_theme_info(theme_name, new_info, existing_info)

    # Determine which preview to use
    if os.path.exists(theme_preview_path):
        preview_path = theme_preview_path
    elif os.path.exists(previews_dir_path):
        preview_path = previews_dir_path
    else:
        print(f"Warning: No preview found for theme {theme_name}")
        new_info["INVALID"] = "No preview.png file found"
        return merge_theme_info(theme_name, new_info, existing_info)

    # Read manifest file
    try:
        with open(manifest_path, 'r') as f:
            manifest_data = json.load(f)
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON in manifest: {str(e)}"
        print(f"Error: {error_msg}")
        new_info["INVALID"] = error_msg
        return merge_theme_info(theme_name, new_info, existing_info)
    except Exception as e:
        error_msg = f"Error reading manifest: {str(e)}"
        print(f"Error: {error_msg}")
        new_info["INVALID"] = error_msg
        return merge_theme_info(theme_name, new_info, existing_info)

    # Extract author and description
    author = manifest_data.get("theme_info", {}).get("author", "Unknown")
    description = manifest_data.get("theme_info", {}).get("name", theme_name)

    # Create relative paths for catalog
    preview_rel_path = f"Catalog/Themes/previews/{theme_name}.png"
    manifest_rel_path = f"Catalog/Themes/manifests/{theme_name}.json"

    # Find corresponding ZIP file in Uploads directory
    zip_filename = f"{theme_name}.zip"
    zip_path = os.path.join(UPLOADS_DIR, "Themes", zip_filename)

    # Generate URL for the ZIP file
    url = f"{GITHUB_RAW_URL}/Themes/{zip_filename}"

    # Update theme info
    new_info.update({
        "preview_path": preview_rel_path,
        "manifest_path": manifest_rel_path,
        "author": author,
        "description": description,
        "URL": url  # Use "URL" property as requested
    })

    # Merge with existing info to preserve metadata
    return merge_theme_info(theme_name, new_info, existing_info)

def merge_component_info(comp_name, new_info, existing_info=None):
    """Merge new component information with existing info, preserving metadata"""
    if existing_info is None:
        comp_info = OrderedDict()
    else:
        # Start with existing info to preserve all fields
        comp_info = OrderedDict(existing_info)

    # Update with new information
    for key, value in new_info.items():
        comp_info[key] = value

    # Always preserve repository metadata if it exists
    if "repository" in existing_info and "repository" not in new_info:
        comp_info["repository"] = existing_info["repository"]
    if "commit" in existing_info and "commit" not in new_info:
        comp_info["commit"] = existing_info["commit"]

    # If pull_now is set to true, DO NOT change it - let process_repos.py handle it
    # If pull_now is not present, don't add it (direct uploads)
    if "pull_now" in existing_info and existing_info["pull_now"] == "true":
        comp_info["pull_now"] = "true"

    return comp_info

def extract_component_info(component_path, component_type, existing_info=None):
    """Extract component information from the component directory and preview/manifest"""
    component_name = os.path.basename(component_path)

    # Start with minimal info to extract
    new_info = OrderedDict()
    if "INVALID" in new_info:
        del new_info["INVALID"]

    # Check for manifest in the component directory
    comp_manifest_path = os.path.join(component_path, "manifest.json")
    comp_preview_path = os.path.join(component_path, "preview.png")

    # Check for manifest in the manifests directory
    manifests_dir_path = os.path.join(COMPONENTS_DIR, component_type, "manifests", f"{component_name}.json")

    # Check for preview in the previews directory
    previews_dir_path = os.path.join(COMPONENTS_DIR, component_type, "previews", f"{component_name}.png")

    # Determine which manifest to use
    if os.path.exists(comp_manifest_path):
        manifest_path = comp_manifest_path
    elif os.path.exists(manifests_dir_path):
        manifest_path = manifests_dir_path
    else:
        print(f"Warning: No manifest found for component {component_name} of type {component_type}")
        new_info["INVALID"] = "No manifest.json file found"
        return merge_component_info(component_name, new_info, existing_info)

    # Determine which preview to use
    if os.path.exists(comp_preview_path):
        preview_path = comp_preview_path
    elif os.path.exists(previews_dir_path):
        preview_path = previews_dir_path
    else:
        print(f"Warning: No preview found for component {component_name} of type {component_type}")
        new_info["INVALID"] = "No preview.png file found"
        return merge_component_info(component_name, new_info, existing_info)

    # Read manifest file
    try:
        with open(manifest_path, 'r') as f:
            manifest_data = json.load(f)
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON in manifest: {str(e)}"
        print(f"Error: {error_msg}")
        new_info["INVALID"] = error_msg
        return merge_component_info(component_name, new_info, existing_info)
    except Exception as e:
        error_msg = f"Error reading manifest: {str(e)}"
        print(f"Error: {error_msg}")
        new_info["INVALID"] = error_msg
        return merge_component_info(component_name, new_info, existing_info)

    # Extract author and description
    author = manifest_data.get("component_info", {}).get("author", "Unknown")
    description = manifest_data.get("component_info", {}).get("name", component_name)

    # Create relative paths for catalog
    preview_rel_path = f"Catalog/Components/{component_type}/previews/{component_name}.png"
    manifest_rel_path = f"Catalog/Components/{component_type}/manifests/{component_name}.json"

    # Find corresponding ZIP file in Uploads directory
    zip_filename = f"{component_name}.zip"
    zip_path = os.path.join(UPLOADS_DIR, "Components", component_type, zip_filename)

    # Generate URL for the ZIP file
    url = f"{GITHUB_RAW_URL}/Components/{component_type}/{zip_filename}"

    # Extract supported systems for overlays
    systems = None
    if component_type == "Overlays":
        # Try to get systems from manifest if available
        if "content" in manifest_data and "systems" in manifest_data["content"]:
            try:
                systems = manifest_data["content"]["systems"]
                if isinstance(systems, list):
                    systems.sort()  # Sort alphabetically
            except Exception as e:
                print(f"Error extracting systems from manifest: {str(e)}")

    # Add this to extract_component_info when processing Wallpapers
    if component_type == "Wallpapers":
        # Only set this if we detect it - don't override existing info
        if os.path.exists(os.path.join(component_path, "ListWallpapers")):
            new_info["has_list_wallpapers"] = True

    # Update component info
    new_info.update({
        "preview_path": preview_rel_path,
        "manifest_path": manifest_rel_path,
        "author": author,
        "description": description,
        "URL": url  # Use "URL" property as requested
    })

    # Add systems for overlays
    if systems:
        new_info["systems"] = systems

    # Merge with existing info to preserve metadata
    return merge_component_info(component_name, new_info, existing_info)

def main():
    """Main function to build the catalog"""
    # Create necessary directories
    os.makedirs(CATALOG_DIR, exist_ok=True)

    # Load existing catalog
    catalog = load_existing_catalog()

    # Process themes
    if os.path.exists(THEMES_DIR):
        # First, scan filesystem for themes
        processed_themes = set()
        for theme_entry in os.listdir(THEMES_DIR):
            theme_path = THEMES_DIR / theme_entry
            if os.path.isdir(theme_path) and not theme_entry.startswith('.') and theme_entry not in ['previews', 'manifests']:
                # Get existing theme info if available
                existing_info = catalog["themes"].get(theme_entry)

                # Process theme
                theme_info = extract_theme_info(theme_path, existing_info)
                if theme_info:
                    catalog["themes"][theme_entry] = theme_info
                    processed_themes.add(theme_entry)

        # Now handle repository-based themes that might not be on filesystem
        for theme_name, theme_info in list(catalog["themes"].items()):
            if theme_name not in processed_themes and "repository" in theme_info and "commit" in theme_info:
                # Preserve repository-based themes - DO NOT REMOVE THEM
                print(f"Preserving repository-based theme: {theme_name}")
                processed_themes.add(theme_name)
            # Only remove if not repository-based AND not on filesystem AND not marked invalid
            elif theme_name not in processed_themes and "repository" not in theme_info and "INVALID" not in theme_info:
                # Theme was removed from filesystem and isn't repository-based
                print(f"Removing theme that no longer exists: {theme_name}")
                del catalog["themes"][theme_name]

    # Process components
    if os.path.exists(COMPONENTS_DIR):
        for comp_type in COMPONENT_TYPES.keys():
            component_dir = COMPONENTS_DIR / comp_type
            comp_type_lower = COMPONENT_TYPES[comp_type]

            # Track which components we've processed
            processed_components = set()

            if os.path.exists(component_dir):
                for component_entry in os.listdir(component_dir):
                    component_path = component_dir / component_entry
                    if os.path.isdir(component_path) and not component_entry.startswith('.') and component_entry not in ['previews', 'manifests']:
                        # Get existing component info if available
                        existing_info = catalog["components"][comp_type_lower].get(component_entry)

                        # Process component
                        component_info = extract_component_info(component_path, comp_type, existing_info)
                        if component_info:
                            catalog["components"][comp_type_lower][component_entry] = component_info
                            processed_components.add(component_entry)

            # Now handle repository-based components that might not be on filesystem
            for comp_name, comp_info in list(catalog["components"][comp_type_lower].items()):
                if comp_name not in processed_components and "repository" in comp_info and "commit" in comp_info:
                    # Preserve repository-based components - DO NOT REMOVE THEM
                    print(f"Preserving repository-based component: {comp_name}")
                    processed_components.add(comp_name)
                # Only remove if not repository-based AND not on filesystem AND not marked invalid
                elif comp_name not in processed_components and "repository" not in comp_info and "INVALID" not in comp_info:
                    # Component was removed from filesystem and isn't repository-based
                    print(f"Removing component that no longer exists: {comp_name}")
                    del catalog["components"][comp_type_lower][comp_name]

    # Update timestamp
    catalog["last_updated"] = datetime.utcnow().isoformat() + "Z"

    # Write catalog.json
    catalog_path = CATALOG_DIR / "catalog.json"
    with open(catalog_path, 'w') as f:
        json.dump(catalog, f, indent=2)

    print(f"Catalog updated successfully at {datetime.utcnow().isoformat()}Z")

if __name__ == "__main__":
    main()