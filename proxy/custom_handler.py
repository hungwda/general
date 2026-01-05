"""
Custom LiteLLM Proxy Handler for Modifying max_tokens
This handler intercepts requests before they're sent to the LLM provider
and modifies the max_tokens parameter.
"""

from litellm.integrations.custom_logger import CustomLogger
from litellm.proxy.proxy_server import UserAPIKeyAuth, DualCache
from typing import Literal, Optional
import os


class MaxTokensModifier(CustomLogger):
    """
    Custom handler that modifies max_tokens in requests before sending to LLM providers.

    You can configure the max_tokens value via:
    1. Environment variable: MAX_TOKENS_OVERRIDE
    2. Default value in the code
    """

    def __init__(self, default_max_tokens: Optional[int] = None):
        """
        Initialize the handler.

        Args:
            default_max_tokens: Default max_tokens value to use if not set via environment
        """
        super().__init__()
        # Get max_tokens from environment or use default
        self.max_tokens = int(os.getenv("MAX_TOKENS_OVERRIDE", default_max_tokens or 2048))
        print(f"MaxTokensModifier initialized with max_tokens={self.max_tokens}")

    async def async_pre_call_hook(
        self,
        user_api_key_dict: UserAPIKeyAuth,
        cache: DualCache,
        data: dict,
        call_type: Literal[
            "completion",
            "text_completion",
            "embeddings",
            "image_generation",
            "moderation",
            "audio_transcription"
        ]
    ):
        """
        Hook called before making LLM API calls.
        Modifies the max_tokens parameter in the request data.

        Args:
            user_api_key_dict: User authentication information
            cache: Cache instance
            data: Request data dictionary that will be sent to the LLM
            call_type: Type of API call being made

        Returns:
            Modified data dictionary with updated max_tokens
        """
        # Only modify completion requests (not embeddings, etc.)
        if call_type in ["completion", "text_completion"]:
            original_max_tokens = data.get("max_tokens")

            # Replace max_tokens with our configured value
            data["max_tokens"] = self.max_tokens

            print(f"Modified max_tokens: {original_max_tokens} -> {self.max_tokens}")
            print(f"Request data: model={data.get('model')}, max_tokens={data.get('max_tokens')}")

        return data


# Example: Custom handler with different strategies
class ConditionalMaxTokensModifier(CustomLogger):
    """
    Advanced handler that modifies max_tokens based on conditions.
    Examples:
    - Different max_tokens for different models
    - Different max_tokens for different users
    - Respect original max_tokens if within limits
    """

    def __init__(self):
        super().__init__()
        # Configure max_tokens per model
        self.model_max_tokens = {
            "gpt-4": 4096,
            "gpt-3.5-turbo": 2048,
            "claude-3-opus": 4096,
            "claude-3-sonnet": 4096,
            "claude-3-haiku": 4096,
        }
        self.default_max_tokens = 2048
        self.max_allowed_tokens = 8192  # Maximum limit

    async def async_pre_call_hook(
        self,
        user_api_key_dict: UserAPIKeyAuth,
        cache: DualCache,
        data: dict,
        call_type: Literal[
            "completion",
            "text_completion",
            "embeddings",
            "image_generation",
            "moderation",
            "audio_transcription"
        ]
    ):
        """
        Conditionally modify max_tokens based on model and constraints.
        """
        if call_type not in ["completion", "text_completion"]:
            return data

        model = data.get("model", "")
        original_max_tokens = data.get("max_tokens")

        # Strategy 1: Use model-specific max_tokens
        # Find matching model configuration
        configured_max_tokens = self.default_max_tokens
        for model_prefix, max_tokens in self.model_max_tokens.items():
            if model_prefix in model:
                configured_max_tokens = max_tokens
                break

        # Strategy 2: If original max_tokens is set, respect it but cap at max_allowed
        if original_max_tokens:
            new_max_tokens = min(original_max_tokens, self.max_allowed_tokens)
        else:
            new_max_tokens = configured_max_tokens

        data["max_tokens"] = new_max_tokens

        print(f"ConditionalMaxTokensModifier: model={model}, "
              f"original={original_max_tokens}, new={new_max_tokens}")

        return data
