# Epoch Semantic Versioning

This project uses **Epoch Semantic Versioning** as proposed by [Anthony Fu](https://antfu.me/posts/epoch-semver).

## Format

`{EPOCH * 1000 + MAJOR}.MINOR.PATCH`

Where:
- **EPOCH**: Increment for significant or groundbreaking changes (new eras)
- **MAJOR**: Increment for minor incompatible API changes 
- **MINOR**: Increment for backwards-compatible feature additions
- **PATCH**: Increment for backwards-compatible bug fixes

## Current Version: `1.0.0`

This translates to:
- **EPOCH**: 0 (no epoch yet - this is the initial era)
- **MAJOR**: 1 (first stable major version)
- **MINOR**: 0 (no new features since major)
- **PATCH**: 0 (no patches since minor)

## Version History

### Epoch 0 (Initial Era)
- `1.0.0` - Initial stable release of Canvas AI Dashboard

## Future Epochs

When we reach significant milestones, we might introduce new epochs:

- **Epoch 1** (`1000.0.0`) - Major architectural overhaul, complete UI/UX redesign
- **Epoch 2** (`2000.0.0`) - Next-generation AI integration, revolutionary features

## Version Bumping Rules

### For PATCH (bug fixes):
```bash
# 1.0.0 → 1.0.1
git tag v1.0.1
```

### For MINOR (new features):
```bash
# 1.0.1 → 1.1.0  
git tag v1.1.0
```

### For MAJOR (breaking changes):
```bash
# 1.1.0 → 2.0.0
git tag v2.0.0
```

### For EPOCH (groundbreaking changes):
```bash
# 999.x.x → 1000.0.0
git tag v1000.0.0
```

## Benefits

1. **Clear Communication**: Distinguishes between technical breaking changes (MAJOR) and significant product changes (EPOCH)
2. **Progressive Updates**: Allows for smaller, more frequent breaking changes without version number inflation
3. **Marketing Clarity**: EPOCH versions can have codenames and be used for major announcements
4. **Backward Compatibility**: Still follows SemVer rules, works with all existing tools

## Tools Integration

This versioning scheme works seamlessly with:
- npm/pip version ranges (`^1.0.0`, `~1.0.0`)
- Package managers (pip, npm, etc.)
- Dependency resolution
- Automated versioning tools
