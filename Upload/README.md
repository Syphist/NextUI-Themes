# Theme/Component Submission Guide

Before submitting, make sure you've taken a look at the documentation:


- [Theme Documentation](https://github.com/Leviathanium/NextUI-Theme-Manager/blob/main/documents/THEMES.md)
- [Theme Creation Guide](https://github.com/Leviathanium/NextUI-Theme-Manager/blob/main/documents/THEME_BUILDING.md)
- [Component Documentation](https://github.com/Leviathanium/NextUI-Theme-Manager/blob/main/documents/COMPONENTS.md)
- [Component Creation Guide](https://github.com/Leviathanium/NextUI-Theme-Manager/blob/main/documents/COMPONENT_BUILDING.md)

Once you have your theme or component package (`.theme`, `.icon`, `.bg`, etc), you submit the package using a Github pull request using `push.json`. 

## Submission Methods

We offer **three ways** to submit your theme or component:

### Option 1: Direct Repository Submission

If your theme is stored in a Git repository, submit it by providing the repository details:


```json5
{
  "submission": [
    {
      "type": "theme",
      "name": "Your-Theme.theme",
      "author": "Your Name",
      "submission_method": "repository",
      "url": "https://github.com/yourusername/your-theme-repo",
      "commit": "commit-hash-to-use",
      "branch": "main"
    }
  ]
}
```

### Option 2: Direct Upload (For themes under 25MB)

For smaller themes, you can upload the zip file directly:

1. Place your theme zip file in this `Upload` directory
2. Name the file exactly as specified in your push.json. **NOTE:** Don't include the `.zip` in the `"name"` field, as you can see below.
3. Update `push.json` with your theme details:

```json5
{
  "submission": [
    {
      "type": "theme",
      "name": "Your-Theme.theme",
      "author": "Your Name",
      "submission_method": "zip"
    }
  ]
}
```

### Option 3: External Hosting (For large themes over 25MB)

For themes larger than GitHub's 25MB limit, host your zip file externally:

1. Upload your theme zip to a file hosting service (Google Drive, Dropbox, etc.)
2. Get a direct download link to your file
3. Update `push.json` with your theme details and download URL:

```json5
{
  "submission": [
    {
      "type": "theme",
      "name": "Your-Theme.theme",
      "author": "Your Name",
      "submission_method": "url",
      "url": "https://direct-download-url-to-your-file.zip"
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
