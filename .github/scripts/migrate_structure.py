#!/usr/bin/env python3
"""
One-time migration script to convert from the old structure to the new structure.
- Rename "Uploads" to "Packages"
- Flatten the directory structure by removing "Components" subdirectory
- Create "Upload" directory with initial push.json and OPTIONS.md
"""

import os
import json
import shutil
from pathlib import Path

# Base paths
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
OLD_UPLOADS_DIR = REPO_ROOT / "Uploads"
NEW_PACKAGES_DIR = REPO_ROOT / "Packages"
NEW_UPLOAD_DIR = REPO_ROOT / "Upload"
CATALOG_DIR = REPO_ROOT / "Catalog"

# Component types
COMPONENT_TYPES = {
    "Wallpapers": ".bg",
    "Icons": ".icon",
    "Accents": ".acc",
    "LEDs": ".led",
    "Fonts": ".font",
    "Overlays": ".over"
}

def create_directory_structure():
    """Create the new directory structure"""
    # Create Upload directory and initial files
    os.makedirs(NEW_UPLOAD_DIR, exist_ok=True)

    # Create initial push.json
    push_json = {
        "submission": []
    }
    with open(NEW_UPLOAD_DIR / "push.json", 'w') as f:
        json.dump(push_json, f, indent=2)

    # Create OPTIONS.md
    options_md = """# Submission Options

Each entry in the `push.json` file should have the following fields:

- `type`: Type of package. Can be one of:
  - `theme`: Full theme package
  - `wallpaper`: Background image
  - `icon`: Icon pack
  - `accent`: UI color scheme
  - `led`: LED effect
  - `font`: Custom font
  - `overlay`: System-specific overlay

- `name`: Package name with its extension (e.g., "MyTheme.theme", "MyWallpaper.bg")

- `submission_method`: Either "repository" or "zip"
  - `repository`: Pull from a Git repository
  - `zip`: Use a zip file placed in the `Upload` directory

- `repository_url`: URL of the Git repository (use "None" if submission_method is "zip")

- `commit`: Commit hash to use (use "None" if submission_method is "zip")

- `branch`: Branch to use (use "None" if submission_method is "zip")

## Example:

```json
{
  "submission": [
    {
      "type": "theme",  
      "name": "MyTheme.theme",
      "submission_method": "repository",
      "repository_url": "https://github.com/user/theme-repo",
      "commit": "abcdef123456",
      "branch": "main"
    },
    {
      "type": "wallpaper",
      "name": "MyWallpaper.bg",
      "submission_method": "zip",
      "repository_url": "None",
      "commit": "None",
      "branch": "None"
    }
  ]
}
```

Note: If you're updating an existing theme or component, use the same name as before. The system will automatically replace the old version.
"""
    with open(NEW_UPLOAD_DIR / "OPTIONS.md", 'w') as f:
        f.write(options_md)

    # Create Packages directory and subdirectories
    os.makedirs(NEW_PACKAGES_DIR, exist_ok=True)
    os.makedirs(NEW_PACKAGES_DIR / "themes", exist_ok=True)
    for component_type in COMPONENT_TYPES.keys():
        os.makedirs(NEW_PACKAGES_DIR / component_type.lower(), exist_ok=True)

def migrate_content():
    """Migrate content from old structure to new structure"""
    if not OLD_UPLOADS_DIR.exists():
        print("No old Uploads directory found, skipping content migration")
        return

    # Migrate theme zips
    old_themes_dir = OLD_UPLOADS_DIR / "Themes"
    if old_themes_dir.exists():
        for item in old_themes_dir.glob("*.theme.zip"):
            shutil.copy2(item, NEW_PACKAGES_DIR / "themes" / item.name)
            print(f"Migrated {item.name} to Packages/themes/")

    # Migrate component zips
    old_components_dir = OLD_UPLOADS_DIR / "Components"
    if old_components_dir.exists():
        for component_type, extension in COMPONENT_TYPES.items():
            old_comp_dir = old_components_dir / component_type
            if old_comp_dir.exists():
                for item in old_comp_dir.glob(f"*{extension}.zip"):
                    shutil.copy2(item, NEW_PACKAGES_DIR / component_type.lower() / item.name)
                    print(f"Migrated {item.name} to Packages/{component_type.lower()}/")

def update_catalog_urls():
    """Update URLs in catalog.json to use the new paths"""
    catalog_path = CATALOG_DIR / "catalog.json"
    if not catalog_path.exists():
        print("No catalog.json found, skipping URL updates")
        return

    try:
        with open(catalog_path, 'r') as f:
            catalog = json.load(f)

        # Update theme URLs
        for theme_name, theme_info in catalog.get("themes", {}).items():
            if "URL" in theme_info:
                old_url = theme_info["URL"]
                new_url = old_url.replace("Uploads/Themes", "Packages/themes")
                theme_info["URL"] = new_url

        # Update component URLs
        for comp_type_lower, components in catalog.get("components", {}).items():
            for comp_name, comp_info in components.items():
                if "URL" in comp_info:
                    old_url = comp_info["URL"]
                    # Find the matching component type
                    for comp_type, extension in COMPONENT_TYPES.items():
                        if extension[1:] == comp_type_lower:  # Remove the dot from extension
                            new_url = old_url.replace(f"Uploads/Components/{comp_type}", f"Packages/{comp_type.lower()}")
                            comp_info["URL"] = new_url
                            break

        with open(catalog_path, 'w') as f:
            json.dump(catalog, f, indent=2)

        print("Updated URLs in catalog.json")
    except Exception as e:
        print(f"Error updating catalog URLs: {e}")

def main():
    """Main function"""
    print("Starting migration to new directory structure")

    # Create new directory structure
    create_directory_structure()

    # Migrate content
    migrate_content()

    # Update catalog URLs
    update_catalog_urls()

    # Rename the old Uploads directory if migration was successful
    if OLD_UPLOADS_DIR.exists():
        # First, make a backup
        backup_dir = REPO_ROOT / "Uploads_backup"
        shutil.copytree(OLD_UPLOADS_DIR, backup_dir)
        print(f"Created backup of Uploads directory at {backup_dir}")

        # Then rename it
        try:
            # Delete OLD_UPLOADS_DIR if the migration was successful
            shutil.rmtree(OLD_UPLOADS_DIR)
            print("Deleted old Uploads directory")
        except Exception as e:
            print(f"Error removing old Uploads directory: {e}")
            print("Please manually delete it after verifying the migration was successful")

    print("Migration complete!")

if __name__ == "__main__":
    main()