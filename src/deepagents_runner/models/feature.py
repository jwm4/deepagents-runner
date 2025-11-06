"""Feature model."""

from pathlib import Path
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

from deepagents_runner.models import FeatureStatus


class Feature(BaseModel):
    """Represents a software feature being developed."""

    id: str = Field(pattern=r"^\d{3}$")
    name: str = Field(pattern=r"^[a-z0-9-]+$")
    branch: str
    spec_dir: Path
    spec_file: Path
    plan_file: Optional[Path] = None
    tasks_file: Optional[Path] = None
    status: FeatureStatus = FeatureStatus.DRAFT
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            Path: str,
            datetime: lambda v: v.isoformat()
        }
