"""Context detection for automatic feature identification."""

import re
from pathlib import Path
from typing import Optional

from deepagents_runner.models.feature import Feature
from deepagents_runner.models import FeatureStatus
from deepagents_runner.utils.git import get_current_branch
from deepagents_runner.utils.exceptions import ContextDetectionError


class ContextDetector:
    """Detects feature context from git branch and filesystem."""

    BRANCH_PATTERN = re.compile(r'^(\d{3})-([a-z0-9-]+)$')

    def __init__(self, workspace_root: Optional[Path] = None):
        """Initialize context detector.

        Args:
            workspace_root: Root directory of the workspace (defaults to cwd)
        """
        self.workspace_root = workspace_root or Path.cwd()
        self.specs_dir = self.workspace_root / "specs"

    def detect_feature(self) -> Optional[Feature]:
        """Auto-detect feature from current git branch.

        Returns:
            Feature object if detected, None otherwise

        Raises:
            ContextDetectionError: If branch pattern matches but feature not found
        """
        branch = get_current_branch()
        if not branch:
            return None

        match = self.BRANCH_PATTERN.match(branch)
        if not match:
            return None

        feature_id = match.group(1)
        feature_name = match.group(2)

        # Build feature paths
        spec_dir = self.specs_dir / f"{feature_id}-{feature_name}"
        spec_file = spec_dir / "spec.md"
        plan_file = spec_dir / "plan.md"
        tasks_file = spec_dir / "tasks.md"

        # Determine status based on what files exist
        status = self._determine_status(spec_file, plan_file, tasks_file)

        return Feature(
            id=feature_id,
            name=feature_name,
            branch=branch,
            spec_dir=spec_dir,
            spec_file=spec_file,
            plan_file=plan_file if plan_file.exists() else None,
            tasks_file=tasks_file if tasks_file.exists() else None,
            status=status
        )

    def _determine_status(
        self,
        spec_file: Path,
        plan_file: Path,
        tasks_file: Path
    ) -> FeatureStatus:
        """Determine feature status from filesystem."""
        if tasks_file.exists():
            return FeatureStatus.TASKED
        elif plan_file.exists():
            return FeatureStatus.PLANNED
        elif spec_file.exists():
            return FeatureStatus.SPECIFIED
        else:
            return FeatureStatus.DRAFT

    def get_or_create_feature(self, feature_id: str, feature_name: str) -> Feature:
        """Get existing feature or create new one.

        Args:
            feature_id: Three-digit feature ID (e.g., "001")
            feature_name: Kebab-case feature name (e.g., "my-feature")

        Returns:
            Feature object
        """
        spec_dir = self.specs_dir / f"{feature_id}-{feature_name}"
        spec_file = spec_dir / "spec.md"
        plan_file = spec_dir / "plan.md"
        tasks_file = spec_dir / "tasks.md"

        branch = f"{feature_id}-{feature_name}"
        status = self._determine_status(spec_file, plan_file, tasks_file)

        return Feature(
            id=feature_id,
            name=feature_name,
            branch=branch,
            spec_dir=spec_dir,
            spec_file=spec_file,
            plan_file=plan_file if plan_file.exists() else None,
            tasks_file=tasks_file if tasks_file.exists() else None,
            status=status
        )
