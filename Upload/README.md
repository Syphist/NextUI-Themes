# Submission Options

Each entry in the `push.json` file should have the following fields:

## Required Fields for All Submissions

- `type`: Type of package. Can be one of:
  - `theme`: Full theme package
  - `wallpaper`: Background image
  - `icon`: Icon pack
  - `accent`: UI color scheme
  - `led`: LED effect
  - `font`: Custom font
  - `overlay`: System-specific overlay

- `name`: Package name with its extension (e.g., "MyTheme.theme", "MyWallpaper.bg")

- `author`: Name of the theme or component creator

- `submission_method`: Either "repository" or "zip"
  - `repository`: Pull from a Git repository
  - `zip`: Use a zip file placed in the `Upload` directory

## Additional Fields for Repository Submissions

These fields are required ONLY when submission_method is "repository":

- `repository_url`: URL of the Git repository

- `commit`: Commit hash to use

- `branch`: Branch to use (optional, defaults to "main")

## Example:

```json
{
  "submission": [
    {
      "type": "theme",  
      "name": "MyTheme.theme",
      "author": "ThemeCreator",
      "submission_method": "repository",
      "repository_url": "https://github.com/user/theme-repo",
      "commit": "abcdef123456",
      "branch": "main"
    },
    {
      "type": "wallpaper",
      "name": "MyWallpaper.bg",
      "author": "WallpaperArtist",
      "submission_method": "zip"
    }
  ]
}
```

## Updating Existing Themes

To update an existing theme or component, use the same name as before. The system will automatically:
1. Find and remove the old version
2. Process the new version in its place
3. Update the catalog entry while preserving metadata

## Requirements for Submissions

All theme and component submissions must include:

1. A `manifest.json` file with proper metadata
2. A `preview.png` image showing what the theme or component looks like

Zipped submissions should be structured as follows:
- The zip file should be named exactly the same as the `name` field in push.json
- Required files (manifest.json, preview.png) should be at the root of the zip or in a single top-level directory