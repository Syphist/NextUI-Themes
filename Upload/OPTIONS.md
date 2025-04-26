# Submission Options

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
