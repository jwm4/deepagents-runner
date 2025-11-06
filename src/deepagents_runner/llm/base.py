"""Base LLM provider interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class Message:
    """Represents a chat message."""

    def __init__(self, role: str, content: str):
        """Initialize message.

        Args:
            role: Message role (system, user, assistant)
            content: Message content
        """
        self.role = role
        self.content = content

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary."""
        return {"role": self.role, "content": self.content}


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, api_key: str, model: Optional[str] = None):
        """Initialize provider.

        Args:
            api_key: API key for the provider
            model: Model name (uses default if not specified)
        """
        self.api_key = api_key
        self.model = model or self.get_default_model()

    @abstractmethod
    def get_default_model(self) -> str:
        """Get the default model name for this provider.

        Returns:
            Default model name
        """
        pass

    @abstractmethod
    async def generate(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate a response from the LLM.

        Args:
            messages: List of messages in the conversation
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Provider-specific options

        Returns:
            Generated response text

        Raises:
            ProviderError: If generation fails
        """
        pass

    @abstractmethod
    async def generate_stream(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """Generate a streaming response from the LLM.

        Args:
            messages: List of messages in the conversation
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Provider-specific options

        Yields:
            Response chunks as they arrive

        Raises:
            ProviderError: If generation fails
        """
        pass

    def supports_streaming(self) -> bool:
        """Check if this provider supports streaming.

        Returns:
            True if streaming is supported
        """
        return True
