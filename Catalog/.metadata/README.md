# .metadata Directory

This directory contains metadata files for all themes and components in the catalog:

- `previews/`: Preview images for all themes and components
- `manifests/`: Manifest files for all themes and components

These files are referenced by the `catalog.json` file and used by the Theme Manager application.
They are duplicates of the files in the individual theme and component directories, 
but organized in a way that avoids filename collisions.

**Note:** Do not modify these files directly. They are automatically maintained by the 
submission processing scripts.
