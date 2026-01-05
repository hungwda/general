"""
Custom LiteLLM Proxy Handler for custom_max_token
This handler intercepts requests before they're sent to the LLM provider
and uses the custom_max_token parameter to set max_tokens.

IMPORTANT: custom_max_token ALWAYS overrides max_tokens, even if max_tokens
is specified in the request. This ensures consistent token control.
"""

from litellm.integrations.custom_logger import CustomLogger
from litellm.proxy.proxy_server import UserAPIKeyAuth, DualCache
from typing import Literal, Optional
import os


class MaxTokensModifier(CustomLogger):
    """
    Custom handler that reads custom_max_token from requests and sets max_tokens.

    IMPORTANT: custom_max_token ALWAYS overrides any max_tokens value in the request.
    If custom_max_token is not provided, uses the configured default.

    You can configure the default custom_max_token value via:
    1. Environment variable: CUSTOM_MAX_TOKEN_DEFAULT
    2. Default value in the code
    """

    def __init__(self, default_custom_max_token: Optional[int] = None):
        """
        Initialize the handler.

        Args:
            default_custom_max_token: Default custom_max_token value to use if not set via environment
        """
        super().__init__()
        # Get custom_max_token default from environment or use default
        self.default_custom_max_token = int(os.getenv("CUSTOM_MAX_TOKEN_DEFAULT", default_custom_max_token or 2048))
        print(f"MaxTokensModifier initialized with default custom_max_token={self.default_custom_max_token}")

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
        Reads custom_max_token from request and sets max_tokens.

        IMPORTANT: custom_max_token ALWAYS overrides max_tokens, even if max_tokens
        is already specified in the request. This ensures consistent token control.

        Args:
            user_api_key_dict: User authentication information
            cache: Cache instance
            data: Request data dictionary that will be sent to the LLM
            call_type: Type of API call being made

        Returns:
            Modified data dictionary with max_tokens set from custom_max_token
        """
        # Only modify completion requests (not embeddings, etc.)
        if call_type in ["completion", "text_completion"]:
            # Get custom_max_token from request, or use default
            custom_max_token = data.pop("custom_max_token", self.default_custom_max_token)
            original_max_tokens = data.get("max_tokens")

            # ALWAYS override max_tokens with custom_max_token value
            # This ensures custom_max_token takes precedence over any existing max_tokens
            data["max_tokens"] = custom_max_token

            print(f"Applied custom_max_token: {custom_max_token}")
            if original_max_tokens:
                print(f"Overrode existing max_tokens: {original_max_tokens} -> {custom_max_token}")
            else:
                print(f"Set max_tokens from custom_max_token: {custom_max_token}")
            print(f"Request data: model={data.get('model')}, max_tokens={data.get('max_tokens')}")

        return data


# Example: Custom handler with different strategies
class ConditionalMaxTokensModifier(CustomLogger):
    """
    Advanced handler that reads custom_max_token and applies conditional logic.

    IMPORTANT: custom_max_token ALWAYS overrides any max_tokens value in the request.

    Examples:
    - Different defaults for different models
    - Cap custom_max_token to prevent excessive values
    - Apply model-specific limits
    """

    def __init__(self):
        super().__init__()
        # Configure default custom_max_token per model
        self.model_custom_max_tokens = {
            "gpt-4": 4096,
            "gpt-3.5-turbo": 2048,
            "claude-3-opus": 4096,
            "claude-3-sonnet": 4096,
            "claude-3-haiku": 4096,
        }
        self.default_custom_max_token = 2048
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
        Conditionally process custom_max_token based on model and constraints.

        IMPORTANT: custom_max_token ALWAYS overrides max_tokens, even if max_tokens
        is already specified in the request.
        """
        if call_type not in ["completion", "text_completion"]:
            return data

        model = data.get("model", "")
        original_max_tokens = data.get("max_tokens")

        # Strategy 1: Use model-specific default custom_max_token
        # Find matching model configuration
        configured_custom_max_token = self.default_custom_max_token
        for model_prefix, custom_max_token in self.model_custom_max_tokens.items():
            if model_prefix in model:
                configured_custom_max_token = custom_max_token
                break

        # Strategy 2: Get custom_max_token from request, or use model-specific default
        custom_max_token = data.pop("custom_max_token", configured_custom_max_token)

        # Strategy 3: Cap at max_allowed to prevent excessive values
        final_max_tokens = min(custom_max_token, self.max_allowed_tokens)

        # ALWAYS override max_tokens with the final value
        # This ensures custom_max_token takes precedence over any existing max_tokens
        data["max_tokens"] = final_max_tokens

        if original_max_tokens and original_max_tokens != final_max_tokens:
            print(f"ConditionalMaxTokensModifier: Overrode max_tokens {original_max_tokens} with {final_max_tokens}")
        print(f"ConditionalMaxTokensModifier: model={model}, "
              f"custom_max_token={custom_max_token}, final_max_tokens={final_max_tokens}")

        return data
