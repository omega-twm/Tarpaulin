# Utils Directory - Versioning Scripts

This directory contains the automated semantic versioning utilities.

## Scripts:

### `semver.py` - **All-in-One Semantic Versioning Tool**
- **Purpose**: Complete conventional commits & semantic versioning solution
- **Usage**: 
  - `python3 utils/semver.py version` - Show current version & epoch breakdown
  - `python3 utils/semver.py analyze` - Analyze commits since last tag
  - `python3 utils/semver.py tag [patch|minor|major|epoch]` - Create version tag
  - `python3 utils/semver.py auto` - Auto-create tag based on commits
- **Features**: 
  - ✅ Conventional commit parsing
  - ✅ Epoch-based versioning
  - ✅ Tag-only approach (no file modifications)
  - ✅ Development version detection

### `setup_conventional_commits.sh`
- **Purpose**: Setup script for the entire system
- **Usage**: `bash utils/setup_conventional_commits.sh` (from project root)
- **What it does**: Installs git hooks, makes scripts executable, shows usage

## Integration:

- **GitHub Actions**: Uses `semver.py auto` for clean tag-only automation
- **Git Hooks**: Uses `semver.py auto` for immediate local feedback
- **Manual Use**: All commands available for testing/debugging

## Benefits of Consolidation:

✅ **Single script** - Everything in one place  
✅ **No complex imports** - Self-contained  
✅ **Simpler maintenance** - One file to update  
✅ **Clear interface** - All commands in one tool  
✅ **Clean git history** - No automated commits  
✅ **No file conflicts** - CI never modifies source files
