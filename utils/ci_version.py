#!/usr/bin/env python3
"""
Tag-only version management - CI creates tags, no file modifications
"""

import subprocess
import sys
import os

# Add the parent directory to the path so we can import from utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.conventional_commits import analyze_commits_for_version_bump, BumpType
from utils.version import get_current_version, bump_version

def create_version_tag_only(bump_type: str) -> str:
    """Create a version tag without modifying any files"""
    current = get_current_version()
    new_version = bump_version(bump_type)
    
    print(f"Creating tag for version bump: {current} → {new_version}")
    
    # Create git tag
    tag = f"v{new_version}"
    try:
        subprocess.run(['git', 'tag', tag], check=True)
        print(f"Created git tag: {tag}")
        return new_version
    except subprocess.CalledProcessError:
        print(f"Failed to create git tag: {tag}")
        return current

def main():
    """CI-friendly version management"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python ci_version.py analyze    # Analyze commits")  
        print("  python ci_version.py tag-only   # Create tag without file changes")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "analyze":
        bump_type, commits = analyze_commits_for_version_bump()
        
        print(f"\nCommits since last version:")
        for commit in commits:
            breaking_indicator = "🔥 " if commit.breaking else ""
            scope_str = f"({commit.scope})" if commit.scope else ""
            print(f"  {breaking_indicator}{commit.type}{scope_str}: {commit.description}")
        
        print(f"\nRecommended version bump: {bump_type.value}")
        return bump_type.value
        
    elif command == "tag-only":
        bump_type, commits = analyze_commits_for_version_bump()
        
        if bump_type == BumpType.NONE:
            print("No version bump needed based on conventional commits")
            sys.exit(0)
        
        new_version = create_version_tag_only(bump_type.value)
        print(f"Tag created: v{new_version}")
        print(f"To push tag: git push origin v{new_version}")
        
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
