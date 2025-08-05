# Utils Directory - Versioning Scripts

This directory contains all the automated semantic versioning utilities.

## Scripts:

### `dynamic_version.py`
- **Purpose**: Get current version from git tags dynamically
- **Usage**: `python3 utils/dynamic_version.py`
- **Returns**: Current version (e.g., "1.1.0" or "1.1.0.dev3" if ahead)

### `ci_version.py` 
- **Purpose**: CI-friendly version management (tag-only)
- **Usage**: 
  - `python3 utils/ci_version.py analyze` - Analyze commits
  - `python3 utils/ci_version.py tag-only` - Create version tag
- **Note**: Only creates tags, never modifies files

### `conventional_commits.py`
- **Purpose**: Parse conventional commits and calculate version bumps
- **Usage**: 
  - `python3 utils/conventional_commits.py analyze` - Show analysis
  - `python3 utils/conventional_commits.py auto` - Auto-bump (legacy)
- **Note**: Contains the core logic for conventional commit parsing

### `version.py`
- **Purpose**: Legacy version management (now tag-only)
- **Usage**: 
  - `python3 utils/version.py show` - Show version info
  - `python3 utils/version.py patch|minor|major|epoch` - Create tags
- **Note**: Now creates tags instead of modifying files

## Integration:

- **GitHub Actions**: Uses `ci_version.py` for clean tag-only automation
- **Git Hooks**: Uses local scripts for immediate tag creation feedback
- **Manual Use**: All scripts can be run manually for testing/debugging

## Benefits:

✅ **Clean git history** - No automated commits  
✅ **No file conflicts** - CI never modifies source files  
✅ **Dynamic versioning** - Version comes from git tags  
✅ **Organized structure** - All utilities in one place
