"""LLM provider factory."""

from typing import Optional

from deepagents_runner.models import ProviderType
from deepagents_runner.llm.base import LLMProvider
from deepagents_runner.llm.anthropic_provider import AnthropicProvider
from deepagents_runner.llm.openai_provider import OpenAIProvider
from deepagents_runner.utils.exceptions import ProviderConfigError


class LLMProviderFactory:
    """Factory for creating LLM provider instances."""

    @staticmethod
    def create(
        provider_type: ProviderType,
        api_key: str,
        model: Optional[str] = None
    ) -> LLMProvider:
        """Create an LLM provider instance.

        Args:
            provider_type: Type of provider to create
            api_key: API key for the provider
            model: Optional model name (uses provider default if not specified)

        Returns:
            LLMProvider instance

        Raises:
            ProviderConfigError: If provider type is invalid
        """
        if provider_type == ProviderType.ANTHROPIC:
            return AnthropicProvider(api_key=api_key, model=model)
        elif provider_type == ProviderType.OPENAI:
            return OpenAIProvider(api_key=api_key, model=model)
        else:
            raise ProviderConfigError(f"Unsupported provider type: {provider_type}")

    @staticmethod
    def create_from_string(
        provider_name: str,
        api_key: str,
        model: Optional[str] = None
    ) -> LLMProvider:
        """Create an LLM provider instance from a string name.

        Args:
            provider_name: Name of the provider ("anthropic" or "openai")
            api_key: API key for the provider
            model: Optional model name (uses provider default if not specified)

        Returns:
            LLMProvider instance

        Raises:
            ProviderConfigError: If provider name is invalid
        """
        try:
            provider_type = ProviderType(provider_name.lower())
            return LLMProviderFactory.create(provider_type, api_key, model)
        except ValueError:
            raise ProviderConfigError(f"Invalid provider name: {provider_name}")
