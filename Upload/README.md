# Theme/Component Submission Guide

Before submitting, make sure you've taken a look at the documentation:


- [Theme Documentation](https://github.com/Leviathanium/NextUI-Theme-Manager/blob/main/documents/THEMES.md)
- [Theme Creation Guide](https://github.com/Leviathanium/NextUI-Theme-Manager/blob/main/documents/THEME_BUILDING.md)
- [Component Documentation](https://github.com/Leviathanium/NextUI-Theme-Manager/blob/main/documents/COMPONENTS.md)
- [Component Creation Guide](https://github.com/Leviathanium/NextUI-Theme-Manager/blob/main/documents/COMPONENT_BUILDING.md)

Once you have your theme or component package (`.theme`, `.icon`, `.bg`, etc), you submit the package using a Github pull request using `push.json`. There are two ways to submit:
1. Submit the URL, commit hash, and branch of your forked template repo, OR
2. Create a `.zip` of the package and uploading it directly to `Upload` with your pull request

When you create your pull request, you modify the `push.json` based on which method you chose. If you're attaching a `.zip`, it must go in the `Uploads` directory along with the changes you make to `push.json`.Your request must contain the following fields:
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

## Examples:

```
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
      "submission_method": "zip"  // <--- Make sure to include the .zip package here inside the Upload directory if you choose to submit a .zip!
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
