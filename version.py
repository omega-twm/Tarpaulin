#!/usr/bin/env python3
"""
Canvas AI Dashboard Version Management
Implements Epoch Semantic Versioning
"""

import re
import subprocess
import sys
from typing import Tuple

def get_current_version() -> str:
    """Get current version from pyproject.toml"""
    try:
        with open('pyproject.toml', 'r') as f:
            content = f.read()
            match = re.search(r'version = "([^"]+)"', content)
            if match:
                return match.group(1)
    except FileNotFoundError:
        pass
    return "1.0.0"

def parse_epoch_version(version: str) -> Tuple[int, int, int, int]:
    """Parse epoch version into components"""
    parts = version.split('.')
    if len(parts) != 3:
        raise ValueError(f"Invalid version format: {version}")
    
    major_with_epoch = int(parts[0])
    minor = int(parts[1])
    patch = int(parts[2])
    
    # Extract epoch and major
    epoch = major_with_epoch // 1000
    major = major_with_epoch % 1000
    
    return epoch, major, minor, patch

def format_epoch_version(epoch: int, major: int, minor: int, patch: int) -> str:
    """Format epoch version components into version string"""
    major_with_epoch = epoch * 1000 + major
    return f"{major_with_epoch}.{minor}.{patch}"

def bump_version(bump_type: str) -> str:
    """Bump version according to type"""
    current = get_current_version()
    epoch, major, minor, patch = parse_epoch_version(current)
    
    if bump_type == "patch":
        patch += 1
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "epoch":
        epoch += 1
        major = 0
        minor = 0
        patch = 0
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")
    
    return format_epoch_version(epoch, major, minor, patch)

def update_pyproject_version(new_version: str):
    """Update version in pyproject.toml"""
    with open('pyproject.toml', 'r') as f:
        content = f.read()
    
    # Update version
    content = re.sub(
        r'version = "[^"]+"',
        f'version = "{new_version}"',
        content
    )
    
    # Update description with epoch info
    epoch, major, minor, patch = parse_epoch_version(new_version)
    epoch_info = f" - Epoch SemVer (E{epoch}.M{major}.{minor}.{patch})"
    content = re.sub(
        r'description = "[^"]*"',
        f'description = "Canvas AI Dashboard{epoch_info}"',
        content
    )
    
    with open('pyproject.toml', 'w') as f:
        f.write(content)

def create_git_tag(version: str):
    """Create git tag for version"""
    tag = f"v{version}"
    try:
        subprocess.run(['git', 'tag', tag], check=True)
        print(f"Created git tag: {tag}")
        return True
    except subprocess.CalledProcessError:
        print(f"Failed to create git tag: {tag}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python version.py <patch|minor|major|epoch>")
        print("       python version.py show")
        print("       python version.py auto  # Use with conventional_commits.py")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "show":
        current = get_current_version()
        epoch, major, minor, patch = parse_epoch_version(current)
        print(f"Current version: {current}")
        print(f"  Epoch: {epoch}")
        print(f"  Major: {major}")
        print(f"  Minor: {minor}")
        print(f"  Patch: {patch}")
        return
    
    if command == "auto":
        print("Auto mode requires conventional_commits.py")
        print("Run: python conventional_commits.py auto")
        sys.exit(1)
    
    if command not in ["patch", "minor", "major", "epoch"]:
        print("Invalid command. Use: patch, minor, major, epoch, auto, or show")
        sys.exit(1)
    
    current = get_current_version()
    new_version = bump_version(command)
    
    print(f"Bumping {command}: {current} → {new_version}")
    
    # Update files
    update_pyproject_version(new_version)
    
    # Create git tag
    if create_git_tag(new_version):
        print(f"Version {new_version} ready!")
        print("To push tag to remote: git push origin v{new_version}")
    else:
        print("Version updated in files, but git tag creation failed")

if __name__ == "__main__":
    main()
