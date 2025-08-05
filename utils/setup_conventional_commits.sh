#!/bin/bash
# Setup script for conventional commits and automated versioning
# Run from project root: bash utils/setup_conventional_commits.sh

echo "🚀 Setting up Conventional Commits and Tag-Only Automated Versioning..."

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Check if we're in the project root (utils directory should exist)
if [ ! -d "utils" ]; then
    echo "❌ Error: Please run this script from the project root"
    echo "Usage: bash utils/setup_conventional_commits.sh"
    exit 1
fi

# Create .git/hooks directory if it doesn't exist
mkdir -p .git/hooks

# Copy post-commit hook (tag-only version)
echo "📋 Installing tag-only post-commit hook..."
cp hooks/post-commit .git/hooks/post-commit
chmod +x .git/hooks/post-commit

# Make versioning scripts executable
chmod +x utils/conventional_commits.py utils/dynamic_version.py utils/ci_version.py utils/version.py

echo "✅ Setup complete!"
echo
echo "📝 Conventional Commit Types (Tag-Only Versioning):"
echo "  feat:     New features (minor version bump)"
echo "  fix:      Bug fixes (patch version bump)"
echo "  perf:     Performance improvements (patch version bump)"
echo "  docs:     Documentation changes (NO version bump)"
echo "  style:    Code style changes (NO version bump)" 
echo "  refactor: Code refactoring (NO version bump)"
echo "  test:     Test changes (NO version bump)"
echo "  chore:    Maintenance tasks (NO version bump)"
echo "  build:    Build system changes (NO version bump)"
echo "  ci:       CI/CD changes (NO version bump)"
echo "  epoch:    Major architectural changes (epoch version bump)"
echo
echo "🔥 Breaking Changes (Major Version Bump):"
echo "  Add '!' after type: feat!: breaking change"
echo "  Or include 'BREAKING CHANGE:' in commit body"
echo
echo "📖 Examples:"
echo "  feat: add new AI query endpoint"
echo "  fix: resolve Canvas API timeout issue"
echo "  feat!: change CLI interface completely"
echo "  docs: update README with new setup instructions"
echo "  chore: update dependencies"
echo
echo "🎯 Testing the setup:"
echo "  python3 utils/ci_version.py analyze"
echo "  python3 utils/dynamic_version.py"
echo "  python3 utils/version.py show"
echo
echo "✨ Tag-only automated versioning is now active!"
echo "   - Commits to main branch will create version tags automatically"
echo "   - No files will be modified by automation"
echo "   - GitHub Actions will validate conventional commits in PRs"
echo "   - Version is derived from git tags dynamically"
