"""Anthropic Claude LLM provider."""

from typing import List, Optional
import anthropic

from deepagents_runner.llm.base import LLMProvider, Message
from deepagents_runner.utils.exceptions import (
    ProviderError,
    ProviderNotAvailableError,
    RateLimitError,
)


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider implementation."""

    DEFAULT_MODEL = "claude-sonnet-4-5"

    def __init__(self, api_key: str, model: Optional[str] = None):
        """Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key
            model: Model name (defaults to Claude 3.5 Sonnet)
        """
        super().__init__(api_key, model)
        try:
            self.client = anthropic.Anthropic(api_key=api_key)
        except Exception as e:
            raise ProviderNotAvailableError(f"Failed to initialize Anthropic client: {e}")

    def get_default_model(self) -> str:
        """Get the default model name."""
        return self.DEFAULT_MODEL

    async def generate(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate a response using Anthropic Claude.

        Args:
            messages: List of messages in the conversation
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate (default: 4096)
            **kwargs: Additional Anthropic-specific options

        Returns:
            Generated response text

        Raises:
            ProviderError: If generation fails
            RateLimitError: If rate limit is exceeded
        """
        try:
            # Convert messages to Anthropic format
            # Anthropic expects system messages separate from conversation
            system_message = None
            conversation_messages = []

            for msg in messages:
                if msg.role == "system":
                    system_message = msg.content
                else:
                    conversation_messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })

            # Build request parameters
            request_params = {
                "model": self.model,
                "messages": conversation_messages,
                "temperature": temperature,
                "max_tokens": max_tokens or 4096,
                **kwargs
            }

            if system_message:
                request_params["system"] = system_message

            # Make API call
            response = self.client.messages.create(**request_params)

            # Extract text from response
            return response.content[0].text

        except anthropic.RateLimitError as e:
            raise RateLimitError(f"Anthropic rate limit exceeded: {e}")
        except anthropic.APIError as e:
            raise ProviderError(f"Anthropic API error: {e}")
        except Exception as e:
            raise ProviderError(f"Unexpected error during Anthropic generation: {e}")

    async def generate_stream(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """Generate a streaming response using Anthropic Claude.

        Args:
            messages: List of messages in the conversation
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate (default: 4096)
            **kwargs: Additional Anthropic-specific options

        Yields:
            Response chunks as they arrive

        Raises:
            ProviderError: If generation fails
            RateLimitError: If rate limit is exceeded
        """
        try:
            # Convert messages to Anthropic format
            system_message = None
            conversation_messages = []

            for msg in messages:
                if msg.role == "system":
                    system_message = msg.content
                else:
                    conversation_messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })

            # Build request parameters
            request_params = {
                "model": self.model,
                "messages": conversation_messages,
                "temperature": temperature,
                "max_tokens": max_tokens or 4096,
                **kwargs
            }

            if system_message:
                request_params["system"] = system_message

            # Make streaming API call
            with self.client.messages.stream(**request_params) as stream:
                for text in stream.text_stream:
                    yield text

        except anthropic.RateLimitError as e:
            raise RateLimitError(f"Anthropic rate limit exceeded: {e}")
        except anthropic.APIError as e:
            raise ProviderError(f"Anthropic API error: {e}")
        except Exception as e:
            raise ProviderError(f"Unexpected error during Anthropic streaming: {e}")
