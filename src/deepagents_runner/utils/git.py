"""Git operations utility."""

from pathlib import Path
from typing import Optional
import subprocess


def get_current_branch() -> Optional[str]:
    """Get the current git branch name."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def is_git_repo() -> bool:
    """Check if current directory is a git repository."""
    try:
        subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            capture_output=True,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def list_branches() -> list[str]:
    """List all git branches."""
    try:
        result = subprocess.run(
            ['git', 'branch', '--list'],
            capture_output=True,
            text=True,
            check=True
        )
        branches = []
        for line in result.stdout.split('\n'):
            line = line.strip()
            if line:
                # Remove the * marker from current branch
                branch = line.lstrip('* ')
                branches.append(branch)
        return branches
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
