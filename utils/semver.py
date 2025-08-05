#!/usr/bin/env python3
"""
Conventional Commits & Automated Semantic Versioning
Tag-only versioning system - no file modifications
"""

import re
import subprocess
import sys
from typing import List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

class BumpType(Enum):
    NONE = "none"
    PATCH = "patch"
    MINOR = "minor" 
    MAJOR = "major"
    EPOCH = "epoch"

@dataclass
class CommitInfo:
    type: str
    scope: Optional[str]
    description: str
    body: Optional[str]
    breaking: bool
    raw_message: str

class ConventionalCommitParser:
    """Parser for conventional commit messages"""
    
    # Conventional commit pattern
    COMMIT_PATTERN = re.compile(
        r'^(?P<type>\w+)(?:\((?P<scope>[^)]+)\))?(?P<breaking>!)?: (?P<description>.+?)(?:\n\n(?P<body>.*))?$',
        re.DOTALL
    )
    
    # Breaking change indicators in body
    BREAKING_PATTERNS = [
        re.compile(r'^BREAKING CHANGE:', re.MULTILINE),
        re.compile(r'^BREAKING-CHANGE:', re.MULTILINE),
    ]
    
    def parse_commit(self, message: str) -> Optional[CommitInfo]:
        """Parse a single commit message"""
        match = self.COMMIT_PATTERN.match(message.strip())
        if not match:
            return None
            
        groups = match.groupdict()
        
        # Check for breaking changes
        breaking = bool(groups.get('breaking'))
        body = groups.get('body', '') or ''
        
        if not breaking and body:
            breaking = any(pattern.search(body) for pattern in self.BREAKING_PATTERNS)
        
        return CommitInfo(
            type=groups['type'].lower(),
            scope=groups.get('scope'),
            description=groups['description'],
            body=body if body else None,
            breaking=breaking,
            raw_message=message
        )
    
    def get_commits_since_tag(self, tag: Optional[str] = None) -> List[str]:
        """Get commit messages since the last tag or all commits if no tag"""
        if tag:
            cmd = ['git', 'log', f'{tag}..HEAD', '--pretty=format:%B%n---COMMIT-END---']
        else:
            cmd = ['git', 'log', '--pretty=format:%B%n---COMMIT-END---']
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            commits = [commit.strip() for commit in result.stdout.split('---COMMIT-END---') if commit.strip()]
            return commits
        except subprocess.CalledProcessError:
            return []
    
    def get_latest_version_tag(self) -> Optional[str]:
        """Get the latest version tag"""
        try:
            result = subprocess.run(
                ['git', 'tag', '-l', 'v*', '--sort=-version:refname'],
                capture_output=True, text=True, check=True
            )
            tags = result.stdout.strip().split('\n')
            return tags[0] if tags and tags[0] else None
        except subprocess.CalledProcessError:
            return None

class VersionBumpCalculator:
    """Calculate version bump based on conventional commits"""
    
    # Mapping of commit types to bump types (following semantic versioning standard)
    TYPE_TO_BUMP = {
        'fix': BumpType.PATCH,      # Bug fixes
        'feat': BumpType.MINOR,     # New features
        'perf': BumpType.PATCH,     # Performance improvements (considered bug fixes)
        # The following types do NOT bump version by default (no functional changes)
        'refactor': BumpType.NONE,  # Code refactoring
        'style': BumpType.NONE,     # Code style/formatting
        'test': BumpType.NONE,      # Test changes
        'docs': BumpType.NONE,      # Documentation changes
        'chore': BumpType.NONE,     # Maintenance tasks
        'build': BumpType.NONE,     # Build system changes
        'ci': BumpType.NONE,        # CI/CD changes
        'revert': BumpType.PATCH,   # Reverts (usually fix something)
    }
    
    # Types that trigger epoch bumps (major architectural changes)
    EPOCH_TYPES = {
        'epoch',  # Custom type for explicit epoch bumps
        'arch',   # Architecture changes
    }
    
    def __init__(self):
        self.parser = ConventionalCommitParser()
    
    def calculate_bump(self, commits: List[str]) -> BumpType:
        """Calculate the required version bump from a list of commits"""
        max_bump = BumpType.NONE
        
        for commit_msg in commits:
            commit = self.parser.parse_commit(commit_msg)
            if not commit:
                continue
            
            bump = self._get_bump_for_commit(commit)
            max_bump = self._max_bump(max_bump, bump)
            
            # Short circuit for epoch bumps
            if max_bump == BumpType.EPOCH:
                break
        
        return max_bump
    
    def _get_bump_for_commit(self, commit: CommitInfo) -> BumpType:
        """Get bump type for a single commit"""
        # Check for explicit epoch types
        if commit.type in self.EPOCH_TYPES:
            return BumpType.EPOCH
        
        # Breaking changes trigger major bumps
        if commit.breaking:
            return BumpType.MAJOR
        
        # Map commit type to bump type
        return self.TYPE_TO_BUMP.get(commit.type, BumpType.NONE)
    
    def _max_bump(self, current: BumpType, new: BumpType) -> BumpType:
        """Return the higher priority bump type"""
        priority = {
            BumpType.NONE: 0,
            BumpType.PATCH: 1,
            BumpType.MINOR: 2,
            BumpType.MAJOR: 3,
            BumpType.EPOCH: 4,
        }
        
        return current if priority[current] >= priority[new] else new

class VersionManager:
    """Manage version tags and calculations"""
    
    def __init__(self):
        self.parser = ConventionalCommitParser()
        self.calculator = VersionBumpCalculator()
    
    def get_current_version(self) -> str:
        """Get current version from git tags"""
        try:
            result = subprocess.run(
                ['git', 'describe', '--tags', '--abbrev=0', '--match=v*'],
                capture_output=True, text=True, check=True
            )
            tag = result.stdout.strip()
            # Remove 'v' prefix if present
            return tag[1:] if tag.startswith('v') else tag
        except subprocess.CalledProcessError:
            return "1.0.0"  # Default version
    
    def get_version_with_dev_suffix(self) -> str:
        """Get version with development suffix if ahead of tag"""
        try:
            # Check if we're exactly on a tag
            subprocess.run(
                ['git', 'describe', '--tags', '--exact-match'],
                capture_output=True, text=True, check=True
            )
            # We're on a tag, use clean version
            return self.get_current_version()
        except subprocess.CalledProcessError:
            # We're ahead of the tag, add dev suffix
            base_version = self.get_current_version()
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
    
    def parse_epoch_version(self, version: str) -> Tuple[int, int, int, int]:
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
    
    def format_epoch_version(self, epoch: int, major: int, minor: int, patch: int) -> str:
        """Format epoch version components into version string"""
        major_with_epoch = epoch * 1000 + major
        return f"{major_with_epoch}.{minor}.{patch}"
    
    def bump_version(self, bump_type: str) -> str:
        """Calculate new version based on bump type"""
        current = self.get_current_version()
        epoch, major, minor, patch = self.parse_epoch_version(current)
        
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
        
        return self.format_epoch_version(epoch, major, minor, patch)
    
    def create_tag(self, version: str) -> bool:
        """Create git tag for version"""
        tag = f"v{version}"
        try:
            subprocess.run(['git', 'tag', tag], check=True)
            print(f"Created git tag: {tag}")
            return True
        except subprocess.CalledProcessError:
            print(f"Failed to create git tag: {tag}")
            return False
    
    def analyze_commits(self) -> Tuple[BumpType, List[CommitInfo]]:
        """Analyze commits since last version tag and determine version bump"""
        # Get latest version tag
        latest_tag = self.parser.get_latest_version_tag()
        print(f"Latest version tag: {latest_tag or 'None found'}")
        
        # Get commits since last tag
        commit_messages = self.parser.get_commits_since_tag(latest_tag)
        
        if not commit_messages:
            print("No commits found since last version tag")
            return BumpType.NONE, []
        
        # Parse commits
        parsed_commits = []
        for msg in commit_messages:
            commit = self.parser.parse_commit(msg)
            if commit:
                parsed_commits.append(commit)
            else:
                print(f"Warning: Non-conventional commit found: {msg[:50]}...")
        
        # Calculate bump
        bump = self.calculator.calculate_bump(commit_messages)
        
        return bump, parsed_commits

def main():
    """Main CLI interface"""
    vm = VersionManager()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python semver.py version                # Show current version")
        print("  python semver.py analyze                # Analyze commits for version bump")
        print("  python semver.py tag [patch|minor|major|epoch]  # Create version tag")
        print("  python semver.py auto                   # Auto-create tag based on commits")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "version":
        current = vm.get_current_version()
        dev_version = vm.get_version_with_dev_suffix()
        
        print(f"Current version: {current}")
        if dev_version != current:
            print(f"Development version: {dev_version}")
        
        # Show epoch breakdown
        try:
            epoch, major, minor, patch = vm.parse_epoch_version(current)
            print(f"  Epoch: {epoch}")
            print(f"  Major: {major}")
            print(f"  Minor: {minor}")
            print(f"  Patch: {patch}")
        except ValueError:
            pass
    
    elif command == "analyze":
        bump_type, commits = vm.analyze_commits()
        
        print(f"\nCommits since last version:")
        for commit in commits:
            breaking_indicator = "🔥 " if commit.breaking else ""
            scope_str = f"({commit.scope})" if commit.scope else ""
            print(f"  {breaking_indicator}{commit.type}{scope_str}: {commit.description}")
        
        print(f"\nRecommended version bump: {bump_type.value}")
        
        if bump_type != BumpType.NONE:
            current = vm.get_current_version()
            new_version = vm.bump_version(bump_type.value)
            print(f"Would create tag: v{new_version} (current: {current})")
    
    elif command == "tag":
        if len(sys.argv) < 3:
            print("Usage: python semver.py tag [patch|minor|major|epoch]")
            sys.exit(1)
        
        bump_type = sys.argv[2]
        if bump_type not in ["patch", "minor", "major", "epoch"]:
            print("Invalid bump type. Use: patch, minor, major, epoch")
            sys.exit(1)
        
        current = vm.get_current_version()
        new_version = vm.bump_version(bump_type)
        
        print(f"Bumping {bump_type}: {current} → {new_version}")
        
        if vm.create_tag(new_version):
            print(f"Version {new_version} ready!")
            print(f"To push tag: git push origin v{new_version}")
        else:
            print("Tag creation failed")
            sys.exit(1)
    
    elif command == "auto":
        bump_type, commits = vm.analyze_commits()
        
        if bump_type == BumpType.NONE:
            print("No version bump needed based on conventional commits")
            sys.exit(0)
        
        current = vm.get_current_version()
        new_version = vm.bump_version(bump_type.value)
        
        print(f"Auto-creating {bump_type.value} tag: {current} → {new_version}")
        
        if vm.create_tag(new_version):
            print(f"Tag created: v{new_version}")
            print(f"To push tag: git push origin v{new_version}")
        else:
            print("Auto-tag creation failed")
            sys.exit(1)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
