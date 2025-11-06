"""OpenAI GPT LLM provider."""

from typing import List, Optional
import openai

from deepagents_runner.llm.base import LLMProvider, Message
from deepagents_runner.utils.exceptions import (
    ProviderError,
    ProviderNotAvailableError,
    RateLimitError,
)


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider implementation."""

    DEFAULT_MODEL = "gpt-4o"

    def __init__(self, api_key: str, model: Optional[str] = None):
        """Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key
            model: Model name (defaults to GPT-4o)
        """
        super().__init__(api_key, model)
        try:
            self.client = openai.OpenAI(api_key=api_key)
        except Exception as e:
            raise ProviderNotAvailableError(f"Failed to initialize OpenAI client: {e}")

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
        """Generate a response using OpenAI GPT.

        Args:
            messages: List of messages in the conversation
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional OpenAI-specific options

        Returns:
            Generated response text

        Raises:
            ProviderError: If generation fails
            RateLimitError: If rate limit is exceeded
        """
        try:
            # Convert messages to OpenAI format
            openai_messages = [msg.to_dict() for msg in messages]

            # Build request parameters
            request_params = {
                "model": self.model,
                "messages": openai_messages,
                "temperature": temperature,
                **kwargs
            }

            if max_tokens:
                request_params["max_tokens"] = max_tokens

            # Make API call
            response = self.client.chat.completions.create(**request_params)

            # Extract text from response
            return response.choices[0].message.content

        except openai.RateLimitError as e:
            raise RateLimitError(f"OpenAI rate limit exceeded: {e}")
        except openai.APIError as e:
            raise ProviderError(f"OpenAI API error: {e}")
        except Exception as e:
            raise ProviderError(f"Unexpected error during OpenAI generation: {e}")

    async def generate_stream(
        self,
        messages: List[Message],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """Generate a streaming response using OpenAI GPT.

        Args:
            messages: List of messages in the conversation
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional OpenAI-specific options

        Yields:
            Response chunks as they arrive

        Raises:
            ProviderError: If generation fails
            RateLimitError: If rate limit is exceeded
        """
        try:
            # Convert messages to OpenAI format
            openai_messages = [msg.to_dict() for msg in messages]

            # Build request parameters
            request_params = {
                "model": self.model,
                "messages": openai_messages,
                "temperature": temperature,
                "stream": True,
                **kwargs
            }

            if max_tokens:
                request_params["max_tokens"] = max_tokens

            # Make streaming API call
            stream = self.client.chat.completions.create(**request_params)

            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except openai.RateLimitError as e:
            raise RateLimitError(f"OpenAI rate limit exceeded: {e}")
        except openai.APIError as e:
            raise ProviderError(f"OpenAI API error: {e}")
        except Exception as e:
            raise ProviderError(f"Unexpected error during OpenAI streaming: {e}")
