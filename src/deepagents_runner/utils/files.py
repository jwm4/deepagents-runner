"""File operations utility."""

import json
from pathlib import Path
from typing import Any, Dict

from deepagents_runner.utils.exceptions import StateLoadError, StateSaveError


def read_json(file_path: Path) -> Dict[str, Any]:
    """Read JSON file with schema versioning support."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        raise StateLoadError(f"State file not found: {file_path}")
    except json.JSONDecodeError as e:
        raise StateLoadError(f"Invalid JSON in {file_path}: {e}")


def write_json(file_path: Path, data: Dict[str, Any]) -> None:
    """Write JSON file atomically."""
    try:
        # Ensure directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write atomically by writing to temp file then renaming
        temp_path = file_path.with_suffix('.tmp')
        with open(temp_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)

        # Atomic rename
        temp_path.replace(file_path)
    except Exception as e:
        raise StateSaveError(f"Failed to write {file_path}: {e}")
