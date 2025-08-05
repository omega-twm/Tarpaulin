#!/usr/bin/env python3
"""
Dynamic versioning - get version from git tags instead of pyproject.toml
"""

import subprocess
import re
from typing import Optional

def get_version_from_git() -> str:
    """Get version from git tags, fallback to default"""
    try:
        # Get the latest version tag
        result = subprocess.run(
            ['git', 'describe', '--tags', '--abbrev=0', '--match=v*'],
            capture_output=True, text=True, check=True
        )
        tag = result.stdout.strip()
        # Remove 'v' prefix if present
        return tag[1:] if tag.startswith('v') else tag
    except subprocess.CalledProcessError:
        # Fallback if no tags exist
        return "1.0.0"

def get_version_with_dev_suffix() -> str:
    """Get version with development suffix if ahead of tag"""
    try:
        # Check if we're exactly on a tag
        subprocess.run(
            ['git', 'describe', '--tags', '--exact-match'],
            capture_output=True, text=True, check=True
        )
        # We're on a tag, use clean version
        return get_version_from_git()
    except subprocess.CalledProcessError:
        # We're ahead of the tag, add dev suffix
        base_version = get_version_from_git()
        try:
            # Get commit count since last tag
            result = subprocess.run(
                ['git', 'rev-list', '--count', f'v{base_version}..HEAD'],
                capture_output=True, text=True, check=True
            )
            commit_count = result.stdout.strip()
            return f"{base_version}.dev{commit_count}"
        except subprocess.CalledProcessError:
            return f"{base_version}.dev0"

if __name__ == "__main__":
    print(get_version_from_git())
