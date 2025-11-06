"""Configuration management for DeepAgents Runner."""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from deepagents_runner.models import ProviderType
from deepagents_runner.utils.exceptions import ProviderConfigError


@dataclass
class RunnerConfig:
    """Configuration for the DeepAgents Runner."""

    # LLM Provider settings
    provider_type: ProviderType
    api_key: str
    model: Optional[str] = None

    # Workspace settings
    workspace_root: Path = Path.cwd()
    specs_dir: Optional[Path] = None
    agents_dir: Optional[Path] = None

    # Runtime settings
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    retry_attempts: int = 2
    retry_backoff_factor: float = 2.0

    def __post_init__(self):
        """Initialize derived paths."""
        if self.specs_dir is None:
            self.specs_dir = self.workspace_root / "specs"

        if self.agents_dir is None:
            # Default to bundled agents
            self.agents_dir = Path(__file__).parent.parent.parent / "agents"


class ConfigLoader:
    """Loads configuration from environment variables and files."""

    @staticmethod
    def load_from_env() -> RunnerConfig:
        """Load configuration from environment variables.

        Environment variables:
            ANTHROPIC_API_KEY: Anthropic API key
            OPENAI_API_KEY: OpenAI API key
            RUNNER_DEFAULT_PROVIDER: Default provider (anthropic or openai)
            RUNNER_MODEL: Model name to use
            RUNNER_TEMPERATURE: Sampling temperature (0.0-1.0)
            RUNNER_MAX_TOKENS: Maximum tokens to generate

        Returns:
            RunnerConfig instance

        Raises:
            ProviderConfigError: If configuration is invalid or incomplete
        """
        # Determine provider and API key
        provider_name = os.getenv("RUNNER_DEFAULT_PROVIDER", "anthropic").lower()

        try:
            provider_type = ProviderType(provider_name)
        except ValueError:
            raise ProviderConfigError(
                f"Invalid RUNNER_DEFAULT_PROVIDER: {provider_name}. "
                "Must be 'anthropic' or 'openai'."
            )

        # Get API key for selected provider
        if provider_type == ProviderType.ANTHROPIC:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ProviderConfigError(
                    "ANTHROPIC_API_KEY environment variable is required "
                    "when using Anthropic provider"
                )
        elif provider_type == ProviderType.OPENAI:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ProviderConfigError(
                    "OPENAI_API_KEY environment variable is required "
                    "when using OpenAI provider"
                )
        else:
            raise ProviderConfigError(f"Unsupported provider: {provider_type}")

        # Load optional settings
        model = os.getenv("RUNNER_MODEL")
        temperature = float(os.getenv("RUNNER_TEMPERATURE", "0.7"))
        max_tokens_str = os.getenv("RUNNER_MAX_TOKENS")
        max_tokens = int(max_tokens_str) if max_tokens_str else None

        return RunnerConfig(
            provider_type=provider_type,
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

    @staticmethod
    def load_from_args(
        provider: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> RunnerConfig:
        """Load configuration from command-line arguments.

        Args:
            provider: Provider name (anthropic or openai)
            model: Model name
            **kwargs: Additional configuration options

        Returns:
            RunnerConfig instance

        Raises:
            ProviderConfigError: If configuration is invalid
        """
        # Start with environment config
        config = ConfigLoader.load_from_env()

        # Override with command-line arguments
        if provider:
            try:
                config.provider_type = ProviderType(provider.lower())
            except ValueError:
                raise ProviderConfigError(f"Invalid provider: {provider}")

            # Re-fetch API key for overridden provider
            if config.provider_type == ProviderType.ANTHROPIC:
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    raise ProviderConfigError(
                        "ANTHROPIC_API_KEY environment variable is required"
                    )
                config.api_key = api_key
            elif config.provider_type == ProviderType.OPENAI:
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ProviderConfigError(
                        "OPENAI_API_KEY environment variable is required"
                    )
                config.api_key = api_key

        if model:
            config.model = model

        # Apply other kwargs
        for key, value in kwargs.items():
            if hasattr(config, key) and value is not None:
                setattr(config, key, value)

        return config
