"""Data models for DeepAgents Runner."""

from enum import Enum


class FeatureStatus(str, Enum):
    """Feature development status."""
    DRAFT = "draft"
    SPECIFIED = "specified"
    PLANNED = "planned"
    TASKED = "tasked"
    IMPLEMENTING = "implementing"
    COMPLETED = "completed"


class CommandType(str, Enum):
    """SpecKit command types."""
    CONSTITUTION = "constitution"
    SPECIFY = "specify"
    CLARIFY = "clarify"
    PLAN = "plan"
    TASKS = "tasks"
    IMPLEMENT = "implement"
    ANALYZE = "analyze"
    CHECKLIST = "checklist"


class WorkflowPhase(str, Enum):
    """Workflow phases."""
    DRAFT = "draft"
    CONSTITUTION = "constitution"
    SPECIFY = "specify"
    CLARIFY = "clarify"
    PLAN = "plan"
    TASKS = "tasks"
    IMPLEMENT = "implement"


class ProviderType(str, Enum):
    """LLM provider types."""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
