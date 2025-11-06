"""Custom exception hierarchy for DeepAgents Runner."""


class RunnerError(Exception):
    """Base exception for all runner errors."""
    pass


class AgentError(RunnerError):
    """Agent-related errors."""
    pass


class AgentDefinitionError(AgentError):
    """Agent definition file is malformed."""
    pass


class AgentExecutionError(AgentError):
    """Agent execution failed."""
    pass


class CommandError(RunnerError):
    """Command execution errors."""
    pass


class CommandExecutionError(CommandError):
    """Command failed during execution."""
    pass


class ContextError(RunnerError):
    """Context detection errors."""
    pass


class ContextDetectionError(ContextError):
    """Failed to detect feature context."""
    pass


class StateError(RunnerError):
    """State management errors."""
    pass


class StateLoadError(StateError):
    """Failed to load state file."""
    pass


class StateSaveError(StateError):
    """Failed to save state file."""
    pass


class ProviderError(RunnerError):
    """LLM provider errors."""
    pass


class ProviderConfigError(ProviderError):
    """Provider configuration is invalid."""
    pass


class ProviderNotAvailableError(ProviderError):
    """Provider API key not set or provider unavailable."""
    pass


class RateLimitError(ProviderError):
    """Provider rate limit exceeded."""
    pass
