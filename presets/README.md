# Presets Directory

This directory stores all presets and screenshots for the Automizer project. These files are meant to be committed to Git so they can be shared across the team and synced via GitHub.

## Structure

```
presets/
├── README.md              # This file
├── presets.json           # Process normalization presets (window positions and sizes)
├── screenshot_presets.json # Screenshot presets (capture areas and linked process presets)
└── screenshots/           # Actual screenshot images (PNG files)
    └── .gitkeep           # Keeps the directory in Git
```

## Files

- `presets.json` - Process normalization presets (window positions and sizes)
- `screenshot_presets.json` - Screenshot presets (capture areas and linked process presets)
- `screenshots/` - Directory containing actual screenshot images (PNG files)

## Usage

The application automatically reads and writes presets to this directory. When you add, update, or remove presets through the application, the changes will be reflected in these JSON files. Screenshots captured by the application are saved to the `screenshots/` subdirectory.

To sync your presets with GitHub:

```bash
git add presets/
git commit -m "Update presets"
git push
```

**Note:** Screenshot images can be large. If you have many screenshots, consider:
- Only committing essential screenshots
- Using Git LFS (Large File Storage) for binary files
- Adding a `.gitignore` rule for screenshots if they shouldn't be versioned

## Format

Both JSON files use the same format with preset ID as the key. Each preset contains:
- `id`: Unique identifier
- `name`: Display name
- Configuration parameters (coordinates, dimensions, etc.)
- `description`: Optional description

Screenshot files are named with their preset ID: `<id>.png`
