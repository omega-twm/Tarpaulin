# Conventional Commits & Automated Semantic Versioning

This project uses [Conventional Commits](https://www.conventionalcommits.org/) to automate semantic versioning with the existing epoch-based versioning system.

## Quick Start

1. **Setup the system:**
   ```bash
   ./setup_conventional_commits.sh
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
| `docs` | Documentation | **Patch** | `docs: update README` |
| `style` | Code style/formatting | **Patch** | `style: fix indentation` |
| `refactor` | Code refactoring | **Patch** | `refactor: simplify query logic` |
| `perf` | Performance improvement | **Patch** | `perf: optimize embeddings` |
| `test` | Test changes | **Patch** | `test: add unit tests` |
| `chore` | Maintenance tasks | **Patch** | `chore: update dependencies` |
| `build` | Build system changes | **Patch** | `build: update pyproject.toml` |
| `ci` | CI/CD changes | **Patch** | `ci: add GitHub Actions` |
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
3. Updates `pyproject.toml` with new version  
4. Creates git tag
5. Shows push command for the tag

### CI/CD Automation (GitHub Actions)

**On Pull Requests:**
- Validates that all commits follow conventional format
- Shows what version bump would be applied

**On Push to Main:**
- Analyzes all commits since last version
- Automatically bumps version if needed
- Commits version changes back to main
- Pushes new git tag

## Manual Commands

### Analyze Commits
```bash
python3 conventional_commits.py analyze
```
Shows commits since last version and recommended bump.

### Auto-bump Version  
```bash
python3 conventional_commits.py auto
```
Automatically applies the calculated version bump.

### Manual Version Bump
```bash
python3 version.py patch   # 1.0.0 → 1.0.1
python3 version.py minor   # 1.0.0 → 1.1.0  
python3 version.py major   # 1.0.0 → 2.0.0
python3 version.py epoch   # 1.0.0 → 1000.0.0
```

### Check Current Version
```bash
python3 version.py show
```

## Epoch Versioning Integration

This system maintains your existing epoch-based versioning:

- **Patch**: `1.0.0` → `1.0.1`
- **Minor**: `1.0.0` → `1.1.0` 
- **Major**: `1.0.0` → `2.0.0`
- **Epoch**: `1.0.0` → `1000.0.0`

The epoch component (`1000.x.y`) represents major architectural changes or complete rewrites.

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

- `conventional_commits.py` - Main analysis and automation logic
- `hooks/post-commit` - Git hook for local automation
- `.github/workflows/semantic-versioning.yml` - GitHub Actions workflow
- `.gitmessage` - Commit message template
- `setup_conventional_commits.sh` - Setup script

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
