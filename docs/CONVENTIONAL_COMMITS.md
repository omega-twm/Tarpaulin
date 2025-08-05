# Conventional Commits & Automated Semantic Versioning

This project uses [Conventional Commits](https://www.conventionalcommits.org/) to automate semantic versioning with the existing epoch-based versioning system.

## Quick Start

1. **Setup the system:**
   ```bash
   bash utils/setup_conventional_commits.sh
   ```

2. **Configure git to use the commit template:**
   ```bash
   git config commit.template .gitmessage
   ```

3. **Start using conventional commits:**
   ```bash
   git commit -m "feat: add new AI query endpoint"
   ```

## Conventional Commit Format

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Commit Types & Version Bumps

| Type | Description | Version Bump | Example |
|------|-------------|--------------|---------|
| `feat` | New feature | **Minor** | `feat: add Canvas integration` |
| `fix` | Bug fix | **Patch** | `fix: resolve API timeout` |
| `perf` | Performance improvement | **Patch** | `perf: optimize embeddings` |
| `docs` | Documentation | **None** | `docs: update README` |
| `style` | Code style/formatting | **None** | `style: fix indentation` |
| `refactor` | Code refactoring | **None** | `refactor: simplify query logic` |
| `test` | Test changes | **None** | `test: add unit tests` |
| `chore` | Maintenance tasks | **None** | `chore: update dependencies` |
| `build` | Build system changes | **None** | `build: update pyproject.toml` |
| `ci` | CI/CD changes | **None** | `ci: add GitHub Actions` |
| `epoch` | Major architectural changes | **Epoch** | `epoch: complete rewrite` |

### Breaking Changes (Major Version Bump)

**Option 1: Add `!` after type:**
```bash
git commit -m "feat!: completely change CLI interface"
```

**Option 2: Include in commit body:**
```bash
git commit -m "feat: change CLI interface

BREAKING CHANGE: The CLI now uses different command syntax"
```

## Automated Versioning

### Local Automation (Git Hooks)

The post-commit hook automatically:
1. Analyzes commits since last version tag
2. Determines appropriate version bump
3. **Creates git tag only** (no file modifications)
4. Shows command to push the tag

**Note**: No files are modified, keeping git history clean.

### CI/CD Automation (GitHub Actions)

**On Pull Requests:**
- Validates that all commits follow conventional format
- Shows what version bump would be applied

**On Push to Main:**
- Analyzes all commits since last version tag
- Creates version tags automatically if needed
- Pushes new git tags to repository
- **No file modifications or automated commits**

## Manual Commands

### Analyze Commits
```bash
python3 utils/ci_version.py analyze
```
Shows commits since last version and recommended bump.

### Create Version Tag
```bash
python3 utils/ci_version.py tag-only
```
Creates a git tag without modifying any files.

### Check Current Version
```bash
python3 utils/dynamic_version.py  # From git tags
python3 utils/version.py show     # Legacy method
```

### Manual Version Bump (Legacy)
```bash
python3 utils/version.py patch   # 1.0.0 → 1.0.1 (creates tag only)
python3 utils/version.py minor   # 1.0.0 → 1.1.0 (creates tag only)  
python3 utils/version.py major   # 1.0.0 → 2.0.0 (creates tag only)
python3 utils/version.py epoch   # 1.0.0 → 1000.0.0 (creates tag only)
```

## Versioning System

This project uses **tag-only semantic versioning** - version numbers come from git tags, not files.

### Current Approach:
- **Version source**: Git tags (e.g., `v1.2.0`)
- **File modifications**: None (clean git history)
- **CI behavior**: Creates tags only, no commits
- **Dynamic versioning**: `python3 utils/dynamic_version.py`

### Legacy File-Based Method:
The old approach that modified `pyproject.toml` has been replaced with this cleaner tag-only system.

## Examples

### Feature Development
```bash
git commit -m "feat: add new Canvas assignment sync"
# Triggers minor version bump: 1.0.0 → 1.1.0
```

### Bug Fix
```bash
git commit -m "fix: resolve timeout in Canvas API calls"  
# Triggers patch version bump: 1.1.0 → 1.1.1
```

### Breaking Change
```bash
git commit -m "feat!: redesign CLI command structure"
# Triggers major version bump: 1.1.1 → 2.0.0
```

### Architecture Change
```bash
git commit -m "epoch: migrate to new AI framework"
# Triggers epoch version bump: 2.0.0 → 1000.0.0
```

## Configuration Files

- `utils/ci_version.py` - CI-friendly tag-only versioning logic
- `utils/dynamic_version.py` - Get version from git tags dynamically  
- `utils/conventional_commits.py` - Main analysis and automation logic
- `utils/version.py` - Legacy version management (now tag-only)
- `hooks/post-commit` - Git hook for local tag-only automation
- `.github/workflows/semantic-versioning.yml` - GitHub Actions workflow
- `.gitmessage` - Commit message template
- `utils/setup_conventional_commits.sh` - Setup script

## Best Practices

1. **Use descriptive commit messages** that explain what changed
2. **Include scope when relevant**: `feat(cli): add new command`
3. **Use breaking change indicators carefully** - they trigger major bumps
4. **Keep commits focused** - one change per commit when possible
5. **Use `chore:` for maintenance** that doesn't affect functionality

## Troubleshooting

### Hook Not Running
```bash
# Make sure the hook is executable
chmod +x .git/hooks/post-commit

# Check if it exists
ls -la .git/hooks/post-commit
```

### Invalid Commit Format
The system will warn about non-conventional commits but won't fail. Use:
```bash
python3 conventional_commits.py analyze
```
to see which commits are being processed.

### Manual Override
If automatic versioning fails, you can always use manual commands:
```bash
python3 version.py patch  # or minor, major, epoch
```
