"""Workflow state model."""

from pathlib import Path
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any

from deepagents_runner.models import WorkflowPhase, CommandType


class CommandRecord(BaseModel):
    """Record of a completed command."""
    command: CommandType
    timestamp: datetime


class WorkflowState(BaseModel):
    """Tracks the current state of a feature's development workflow."""

    feature_id: str
    current_phase: WorkflowPhase
    completed_commands: List[CommandRecord] = []
    suggested_next: Optional[CommandType] = None
    context_data: Dict[str, Any] = {}
    state_file: Path
    last_checkpoint: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            Path: str,
            datetime: lambda v: v.isoformat()
        }
