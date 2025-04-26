#!/usr/bin/env python3
"""
Migration script to move existing previews and manifests to the new .metadata directory structure
and update catalog.json references accordingly.
"""

import os
import json
import shutil
from pathlib import Path

# Base paths
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CATALOG_DIR = REPO_ROOT / "Catalog"
METADATA_DIR = CATALOG_DIR / ".metadata"
CATALOG_PATH = CATALOG_DIR / "catalog.json"

# Component types and their directories
COMPONENT_DIRS = {
    "Themes": ".theme",
    "Wallpapers": ".bg",
    "Icons": ".icon",
    "Accents": ".acc",
    "LEDs": ".led",
    "Fonts": ".font",
    "Overlays": ".over"
}

def create_metadata_directory():
    """Create the .metadata directory structure"""
    os.makedirs(METADATA_DIR / "previews", exist_ok=True)
    os.makedirs(METADATA_DIR / "manifests", exist_ok=True)

    # Add a README.md to explain the purpose of this directory
    readme_content = """# .metadata Directory

This directory contains metadata files for all themes and components in the catalog:

- `previews/`: Preview images for all themes and components
- `manifests/`: Manifest files for all themes and components

These files are referenced by the `catalog.json` file and used by the Theme Manager application.
They are duplicates of the files in the individual theme and component directories, 
but organized in a way that avoids filename collisions.

**Note:** Do not modify these files directly. They are automatically maintained by the 
submission processing scripts.
"""

    with open(METADATA_DIR / "README.md", "w") as f:
        f.write(readme_content)

    print("Created .metadata directory structure")

def migrate_previews_and_manifests():
    """Move existing previews and manifests to the .metadata directory"""
    # Load catalog.json to find existing entries
    if not CATALOG_PATH.exists():
        print("catalog.json not found, skipping migration")
        return

    try:
        with open(CATALOG_PATH, "r") as f:
            catalog = json.load(f)
    except Exception as e:
        print(f"Error loading catalog.json: {e}")
        return

    # Process themes
    migrated_count = 0
    for theme_name, theme_info in catalog.get("themes", {}).items():
        # Get source paths
        theme_dir = CATALOG_DIR / "Themes" / theme_name
        if not theme_dir.exists():
            print(f"Warning: Theme directory not found for {theme_name}, skipping")
            continue

        preview_src = theme_dir / "preview.png"
        manifest_src = theme_dir / "manifest.json"

        if not preview_src.exists() or not manifest_src.exists():
            print(f"Warning: Missing files for {theme_name}, skipping")
            continue

        # Destination paths in .metadata
        preview_dest = METADATA_DIR / "previews" / f"{theme_name}.png"
        manifest_dest = METADATA_DIR / "manifests" / f"{theme_name}.json"

        # Copy files
        shutil.copy2(preview_src, preview_dest)
        shutil.copy2(manifest_src, manifest_dest)

        # Update catalog paths
        theme_info["preview_path"] = str(preview_dest.relative_to(REPO_ROOT))
        theme_info["manifest_path"] = str(manifest_dest.relative_to(REPO_ROOT))

        migrated_count += 1

    # Process components
    for comp_type, comp_items in catalog.get("components", {}).items():
        # Find corresponding component directory
        component_dir_name = None
        for dir_name, extension in COMPONENT_DIRS.items():
            if extension[1:] == comp_type:  # Remove the dot from extension
                component_dir_name = dir_name
                break

        if not component_dir_name:
            print(f"Warning: Unknown component type {comp_type}, skipping")
            continue

        for comp_name, comp_info in comp_items.items():
            # Get source paths
            comp_dir = CATALOG_DIR / component_dir_name / comp_name
            if not comp_dir.exists():
                print(f"Warning: Component directory not found for {comp_name}, skipping")
                continue

            preview_src = comp_dir / "preview.png"
            manifest_src = comp_dir / "manifest.json"

            if not preview_src.exists() or not manifest_src.exists():
                print(f"Warning: Missing files for {comp_name}, skipping")
                continue

            # Destination paths in .metadata
            preview_dest = METADATA_DIR / "previews" / f"{comp_name}.png"
            manifest_dest = METADATA_DIR / "manifests" / f"{comp_name}.json"

            # Copy files
            shutil.copy2(preview_src, preview_dest)
            shutil.copy2(manifest_src, manifest_dest)

            # Update catalog paths
            comp_info["preview_path"] = str(preview_dest.relative_to(REPO_ROOT))
            comp_info["manifest_path"] = str(manifest_dest.relative_to(REPO_ROOT))

            migrated_count += 1

    # Save updated catalog
    try:
        with open(CATALOG_PATH, "w") as f:
            json.dump(catalog, f, indent=2)
        print(f"Updated catalog.json with new metadata paths")
    except Exception as e:
        print(f"Error saving catalog.json: {e}")

    print(f"Migrated {migrated_count} items to .metadata directory")

def cleanup_old_metadata_directories():
    """Remove old previews and manifests directories"""
    old_dirs = []

    # Theme previews and manifests
    theme_previews = CATALOG_DIR / "Themes" / "previews"
    theme_manifests = CATALOG_DIR / "Themes" / "manifests"
    old_dirs.extend([theme_previews, theme_manifests])

    # Component previews and manifests
    for component_dir in COMPONENT_DIRS.keys():
        if component_dir == "Themes":
            continue  # Already handled above

        comp_previews = CATALOG_DIR / component_dir / "previews"
        comp_manifests = CATALOG_DIR / component_dir / "manifests"
        old_dirs.extend([comp_previews, comp_manifests])

    # Remove directories that exist
    removed_count = 0
    for directory in old_dirs:
        if directory.exists():
            try:
                shutil.rmtree(directory)
                print(f"Removed old metadata directory: {directory}")
                removed_count += 1
            except Exception as e:
                print(f"Error removing {directory}: {e}")

    print(f"Removed {removed_count} old metadata directories")

def main():
    """Main function to run the migration"""
    print("Starting migration to .metadata directory structure")

    # Create .metadata directory structure
    create_metadata_directory()

    # Migrate existing previews and manifests
    migrate_previews_and_manifests()

    # Clean up old metadata directories
    cleanup_old_metadata_directories()

    print("Migration complete!")

if __name__ == "__main__":
    main()