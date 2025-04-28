#!/usr/bin/env python3

"""
Simplified gallery generation script that only creates a Featured Themes section
"""

import os
import json
import re
import shutil
from string import Template
from datetime import datetime
from urllib.parse import quote

# Configuration
REPO_URL = "https://github.com/Leviathanium/NextUI-Themes"
RAW_URL = "https://github.com/Leviathanium/NextUI-Themes/raw/main"
CATALOG_PATH = "Catalog/catalog.json"
OUTPUT_DIR = ".github/index"
TEMPLATES_DIR = ".github/templates"
README_PATH = "README.md"
FEATURED_COUNT = 20  # Increased from 3 to 6 since this will be our only section
COLUMNS_PER_ROW = 3
README_GALLERY_PATTERN = r"<!-- GALLERY_START -->.*?<!-- GALLERY_END -->"

# Component types
COMPONENT_TYPES = {
    "themes": {
        "title": "Full Themes",
        "extension": ".theme"
    },
    "wallpapers": {
        "title": "Wallpapers",
        "extension": ".bg"
    },
    "icons": {
        "title": "Icons",
        "extension": ".icon"
    },
    "accents": {
        "title": "Accent Colors",
        "extension": ".acc"
    },
    "fonts": {
        "title": "Fonts",
        "extension": ".font"
    },
    "overlays": {
        "title": "Overlays",
        "extension": ".over"
    }
}

def load_template(template_name):
    """Load a template file from the templates directory"""
    path = os.path.join(TEMPLATES_DIR, template_name)
    with open(path, "r", encoding="utf-8") as f:
        return Template(f.read())

def load_catalog():
    """Load the catalog.json file"""
    try:
        with open(CATALOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading catalog: {e}")
        return None

def ensure_dir(path):
    """Ensure a directory exists"""
    os.makedirs(path, exist_ok=True)

def format_date(date_str):
    """Format a date string for display"""
    try:
        date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return date.strftime("%Y-%m-%d")
    except:
        return date_str

def generate_item_card(item, type_key, width=None):
    """Generate a card for a theme or component"""
    item_template = load_template("item_template.md")

    # Get item metadata
    name = item.get("description", os.path.basename(item.get("manifest_path", "")).replace(".json", ""))
    author = item.get("author", "Unknown")
    updated = format_date(item.get("last_updated", ""))

    # URLs
    preview_url = f"{RAW_URL}/{item.get('preview_path', '')}"
    download_url = item.get("URL", "")

    # Update history URL to use new path structure
    if type_key == "themes":
        history_url = f"{REPO_URL}/commits/main/Catalog/Themes/{name}"
    else:
        component_dir = COMPONENT_TYPES[type_key]["title"]
        history_url = f"{REPO_URL}/commits/main/Catalog/{component_dir}/{name}"

    # Title for hover
    title_parts = []
    if name:
        title_parts.append(f"Name: {name}")
    if author:
        title_parts.append(f"Author: {author}")
    if updated:
        title_parts.append(f"Last updated: {updated}")
    title_parts.append("(Click to download)")

    # Substitute values in template
    return item_template.substitute({
        "COLUMN_WIDTH": width or int(100 / COLUMNS_PER_ROW),
        "COLUMN_SPANNER": "<br/>" if width else "",
        "DOWNLOAD_URL": download_url,
        "PREVIEW_URL": preview_url,
        "TITLE": "&#013;".join(title_parts),
        "NAME": name,
        "AUTHOR": author,
        "UPDATED": updated,
        "HISTORY_URL": history_url,
        "METADATA_ICONS": ""
    })

def generate_grid(items, type_key):
    """Generate a grid of items"""
    grid_template = load_template("grid_template.md")

    rows = []
    current_row = []

    for i, item in enumerate(items):
        current_row.append(generate_item_card(item, type_key))

        if (i + 1) % COLUMNS_PER_ROW == 0 or i == len(items) - 1:
            # Fill the row with empty cells if needed
            while len(current_row) < COLUMNS_PER_ROW:
                current_row.append("")

            rows.append("\n".join(current_row))
            current_row = []

    grid_items = "</tr><tr>\n".join(rows)
    return grid_template.substitute({"GRID_ITEMS": grid_items})

def is_valid_item(item):
    """Check if an item is valid (doesn't have the INVALID flag)"""
    return "INVALID" not in item and "preview_path" in item and "manifest_path" in item

def get_valid_themes(catalog):
    """Get valid themes from the catalog, preserving catalog.json order"""
    # Get items as list of (key, value) pairs to preserve order
    theme_items = list(catalog.get("themes", {}).items())
    # Extract only the values (theme objects) while preserving order
    valid_themes = [item[1] for item in theme_items if is_valid_item(item[1])]
    # No sorting - preserve the insertion order from catalog.json
    return valid_themes  # REMOVED sorting by last_updated

def generate_component_index(component_type, valid_items):
    """Generate an index page for a component type with special handling for overlays"""
    type_info = COMPONENT_TYPES[component_type]
    category_dir = f"{OUTPUT_DIR}/{component_type}"
    ensure_dir(category_dir)

    # Create basic header content
    content = f"# {type_info['title']}\n\n"
    content += f"*{len(valid_items)} available {component_type}*\n\n"

    # Special handling for overlays with system filtering
    if component_type == "overlays":
        # Collect all unique system tags and find icons
        all_systems = set()
        system_icons = {}  # Will store system code -> icon path

        for item in valid_items:
            if "systems" in item:
                # Add all systems to our set
                all_systems.update(item["systems"])

                # Look for system icons in this overlay package
                overlay_name = item.get("description", "").replace(" ", "-")
                overlay_dir = CATALOG_DIR / "Overlays" / overlay_name

                if overlay_dir.exists():
                    # Look for the Systems directory
                    systems_dir = overlay_dir / "Systems"
                    if systems_dir.exists():
                        # Check each system supported by this overlay
                        for system in item["systems"]:
                            # Skip if we already found an icon for this system
                            if system in system_icons:
                                continue

                            # Look for system directory and icon
                            system_dir = systems_dir / system
                            if system_dir.exists():
                                # Try common icon filenames
                                for icon_name in ["icon.png", "overlay.png", "preview.png"]:
                                    icon_path = system_dir / icon_name
                                    if icon_path.exists():
                                        # Found an icon! Store relative path from repo root
                                        rel_path = icon_path.relative_to(REPO_ROOT)
                                        system_icons[system] = f"https://github.com/Leviathanium/NextUI-Themes/raw/main/{rel_path}"
                                        break

        # Sort systems alphabetically
        sorted_systems = sorted(all_systems)

        # Add system navigation section with icons
        if sorted_systems:
            content += "## Filter by System\n\n"
            content += "<div style='display: flex; flex-wrap: wrap; gap: 10px; justify-content: center;'>\n"

            for system in sorted_systems:
                if system in system_icons:
                    # We have an icon for this system
                    content += f"<a href='#{system.lower()}-overlays' style='text-align: center; display: inline-block; margin: 5px;'>\n"
                    content += f"<img src='{system_icons[system]}' alt='{system}' width='64' height='64' style='display: block; margin: 0 auto;'/><br/>\n"
                    content += f"{system}\n</a>\n"
                else:
                    # No icon, just use text
                    content += f"<a href='#{system.lower()}-overlays' style='text-align: center; display: inline-block; margin: 5px;'>\n"
                    content += f"<div style='width: a64px; height: 64px; display: flex; align-items: center; justify-content: center; border: 1px solid #ccc;'>{system}</div>\n"
                    content += f"{system}\n</a>\n"

            content += "</div>\n\n"

            # Generate a section for each system
            for system in sorted_systems:
                # Filter items for this system
                system_items = [item for item in valid_items if "systems" in item and system in item["systems"]]

                if system_items:
                    # Add icon to header if available
                    if system in system_icons:
                        content += f"## <img src='{system_icons[system]}' alt='{system}' width='32' height='32' style='vertical-align: middle;'/> {system} Overlays\n\n"
                    else:
                        content += f"## {system} Overlays\n\n"

                    content += f"*{len(system_items)} overlays available for {system}*\n\n"
                    content += generate_grid(system_items, component_type)
                    content += "\n\n"

        # Add section for overlays without system tags
        unsorted_items = [item for item in valid_items if "systems" not in item]
        if unsorted_items:
            content += "## Other Overlays\n\n"
            content += f"*{len(unsorted_items)} overlays without system tags*\n\n"
            content += generate_grid(unsorted_items, component_type)
    else:
        # For non-overlay components, generate a single grid
        content += generate_grid(valid_items, component_type)

    with open(f"{category_dir}/index.md", "w", encoding="utf-8") as f:
        f.write(content)

def generate_main_index(catalog, featured_themes):
    """Generate a simplified main index page with only featured themes"""
    index_template = """# NextUI Themes Gallery

Browse and download themes and components for NextUI devices.

## Categories

- [Full Themes (.theme)](/.github/index/themes/index.md) - Complete theme packages
- [Wallpapers (.bg)](/.github/index/wallpapers/index.md) - Background image collections
- [Icons (.icon)](/.github/index/icons/index.md) - Custom icon packs
- [Accents (.acc)](/.github/index/accents/index.md) - UI color schemes
- [Fonts (.font)](/.github/index/fonts/index.md) - Custom system fonts
- [Overlays (.over)](/.github/index/overlays/index.md) - System-specific overlays

## Featured Themes

$FEATURED_THEMES
"""

    # Generate featured themes grid
    featured_grid = generate_grid(featured_themes[:FEATURED_COUNT], "themes")

    # Create the main index page
    index_content = Template(index_template).substitute({
        "FEATURED_THEMES": featured_grid
    })

    ensure_dir(OUTPUT_DIR)
    with open(f"{OUTPUT_DIR}/index.md", "w", encoding="utf-8") as f:
        f.write(index_content)

def update_readme_gallery(featured_themes):
    """Update the gallery section in the README with only featured themes"""
    # Read the current README
    try:
        with open(README_PATH, "r", encoding="utf-8") as f:
            readme_content = f.read()
    except Exception as e:
        print(f"Error reading README: {e}")
        return False

    # Generate featured themes grid
    featured_grid = generate_grid(featured_themes[:FEATURED_COUNT], "themes")

    # Create the replacement content
    gallery_content = f"<!-- GALLERY_START -->\n## Featured Themes\n\n{featured_grid}\n\n<div align=\"center\"><h3><a href=\".github/index/index.md\">Browse All Themes</a></h3></div>\n<!-- GALLERY_END -->"

    # Replace the gallery section
    pattern = re.compile(README_GALLERY_PATTERN, re.DOTALL)
    if pattern.search(readme_content):
        updated_readme = pattern.sub(gallery_content, readme_content)

        # Write the updated README
        with open(README_PATH, "w", encoding="utf-8") as f:
            f.write(updated_readme)
        return True
    else:
        print("Gallery section not found in README")
        return False

def main():
    """Main function with simplified gallery structure"""
    print("Generating simplified theme gallery...")

    # Load the catalog
    catalog = load_catalog()
    if not catalog:
        print("Failed to load catalog.json")
        return

    # Clear output directory
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)

    # Get valid themes - now preserving original order
    valid_themes = get_valid_themes(catalog)

    # Generate component indices
    for component_type in COMPONENT_TYPES.keys():
        if component_type == "themes":
            # For themes, use the valid_themes list
            generate_component_index(component_type, valid_themes)
        else:
            # For other components, get their valid items
            # Preserve catalog.json order by getting items as list
            component_items = list(catalog.get("components", {}).get(component_type, {}).items())
            # Extract values while preserving order
            valid_items = [item[1] for item in component_items if is_valid_item(item[1])]
            # REMOVED: No sorting by last_updated
            generate_component_index(component_type, valid_items)

    # Generate main index with only featured themes section
    generate_main_index(catalog, valid_themes)

    # Update README gallery section
    if update_readme_gallery(valid_themes):
        print("Updated README gallery section")

    print("Simplified gallery generation complete!")

if __name__ == "__main__":
    main()