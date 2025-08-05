#!/usr/bin/env python3
"""
Conventional Commits Parser for Automated Semantic Versioning
Integrates with the existing epoch versioning system
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

def analyze_commits_for_version_bump() -> Tuple[BumpType, List[CommitInfo]]:
    """Analyze commits since last version tag and determine version bump"""
    parser = ConventionalCommitParser()
    calculator = VersionBumpCalculator()
    
    # Get latest version tag
    latest_tag = parser.get_latest_version_tag()
    print(f"Latest version tag: {latest_tag or 'None found'}")
    
    # Get commits since last tag
    commit_messages = parser.get_commits_since_tag(latest_tag)
    
    if not commit_messages:
        print("No commits found since last version tag")
        return BumpType.NONE, []
    
    # Parse commits
    parsed_commits = []
    for msg in commit_messages:
        commit = parser.parse_commit(msg)
        if commit:
            parsed_commits.append(commit)
        else:
            print(f"Warning: Non-conventional commit found: {msg[:50]}...")
    
    # Calculate bump
    bump = calculator.calculate_bump(commit_messages)
    
    return bump, parsed_commits

def main():
    """CLI interface for conventional commit analysis"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python conventional_commits.py analyze  # Analyze commits and suggest version bump")
        print("  python conventional_commits.py auto     # Analyze and automatically bump version")
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
        
        if bump_type != BumpType.NONE:
            print(f"\nTo apply this bump, run: python version.py {bump_type.value}")
        
    elif command == "auto":
        bump_type, commits = analyze_commits_for_version_bump()
        
        if bump_type == BumpType.NONE:
            print("No version bump needed based on conventional commits")
            sys.exit(0)
        
        print(f"Auto-bumping version: {bump_type.value}")
        
        # Import and use existing version management
        from version import main as version_main
        
        # Override sys.argv to call version.py with the calculated bump
        original_argv = sys.argv[:]
        sys.argv = ['version.py', bump_type.value]
        
        try:
            version_main()
        finally:
            sys.argv = original_argv
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
