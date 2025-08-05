#!/bin/bash
# Setup script for conventional commits and automated versioning

echo "🚀 Setting up Conventional Commits and Automated Versioning..."

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Create .git/hooks directory if it doesn't exist
mkdir -p .git/hooks

# Copy post-commit hook
echo "📋 Installing post-commit hook..."
cp hooks/post-commit .git/hooks/post-commit
chmod +x .git/hooks/post-commit

# Make conventional_commits.py executable
chmod +x conventional_commits.py

echo "Setup complete!"
echo
echo "Conventional Commit Types:"
echo "  feat:     New features (minor version bump)"
echo "  fix:      Bug fixes (patch version bump)"
echo "  docs:     Documentation changes (patch version bump)"
echo "  style:    Code style changes (patch version bump)" 
echo "  refactor: Code refactoring (patch version bump)"
echo "  perf:     Performance improvements (patch version bump)"
echo "  test:     Test changes (patch version bump)"
echo "  chore:    Maintenance tasks (patch version bump)"
echo "  build:    Build system changes (patch version bump)"
echo "  ci:       CI/CD changes (patch version bump)"
echo "  epoch:    Major architectural changes (epoch version bump)"
echo
echo "Breaking Changes:"
echo "  Add '!' after type: feat!: breaking change"
echo "  Or include 'BREAKING CHANGE:' in commit body"
echo
echo "Examples:"
echo "  feat: add new AI query endpoint"
echo "  fix: resolve Canvas API timeout issue"
echo "  feat!: change CLI interface completely"
echo "  docs: update README with new setup instructions"
echo "  chore: update dependencies"
echo
echo "Testing the setup:"
echo "  python3 conventional_commits.py analyze"
echo "  python3 version.py show"
echo
echo "Automated versioning is now active!"
echo "   - Commits to main branch will trigger automatic version bumps"
echo "   - GitHub Actions will validate conventional commits in PRs"
echo "   - Git tags will be created automatically"
