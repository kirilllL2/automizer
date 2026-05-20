# Presets Directory

This directory stores all presets for the Automizer project. These files are meant to be committed to Git so they can be shared across the team and synced via GitHub.

## Files

- `presets.json` - Process normalization presets (window positions and sizes)
- `screenshot_presets.json` - Screenshot presets (capture areas and linked process presets)

## Usage

The application automatically reads and writes presets to this directory. When you add, update, or remove presets through the application, the changes will be reflected in these JSON files.

To sync your presets with GitHub:

```bash
git add presets/
git commit -m "Update presets"
git push
```

## Format

Both files use JSON format with preset ID as the key. Each preset contains:
- `id`: Unique identifier
- `name`: Display name
- Configuration parameters (coordinates, dimensions, etc.)
- `description`: Optional description
