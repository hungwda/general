# LiteLLM Proxy with custom_max_token Support

This solution provides a custom LiteLLM proxy setup that allows you to use a `custom_max_token` parameter in requests, which will be used to set the `max_tokens` value sent to LLM providers.

**IMPORTANT**: `custom_max_token` **ALWAYS** overrides `max_tokens`, even if `max_tokens` is specified in the request. This ensures consistent token control.

## Overview

The solution uses LiteLLM's custom callback system with the `async_pre_call_hook` to intercept requests before they reach the LLM provider. This allows you to:

- Use `custom_max_token` parameter in requests to control `max_tokens`
- Override any `max_tokens` value with `custom_max_token` (takes precedence)
- Set different default `custom_max_token` based on the model
- Cap `custom_max_token` to prevent excessive costs
- Apply conditional logic based on user, model, or other criteria

## Files

- **custom_handler.py**: Contains custom callback handlers for processing custom_max_token
  - `MaxTokensModifier`: Simple handler that reads custom_max_token and sets max_tokens
  - `ConditionalMaxTokensModifier`: Advanced handler with model-specific defaults and conditional logic
- **proxy_config.yaml**: LiteLLM proxy configuration file
- **requirements.txt**: Python dependencies
- **.env.example**: Example environment variables configuration
- **start_proxy.sh**: Shell script to start the proxy server
- **test_proxy.py**: Test script demonstrating usage

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file and configure your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
LITELLM_MASTER_KEY=your_master_key_here
CUSTOM_MAX_TOKEN_DEFAULT=2048
```

### 3. Configure the Proxy

Edit `proxy_config.yaml` to:
- Add your LLM models
- Choose which handler to use (MaxTokensModifier or ConditionalMaxTokensModifier)
- Adjust other settings as needed

## Usage

### Starting the Proxy

#### Option 1: Use the startup script

```bash
./start_proxy.sh
```

#### Option 2: Run directly

```bash
export CUSTOM_MAX_TOKEN_DEFAULT=2048
litellm --config proxy_config.yaml --port 4000
```

The proxy will start on `http://localhost:4000`

### Making Requests

Once the proxy is running, you can send requests to it using the OpenAI SDK or any HTTP client:

#### Using OpenAI Python SDK

```python
import openai

client = openai.OpenAI(
    api_key="your-litellm-key",  # Your LiteLLM proxy key
    base_url="http://localhost:4000"
)

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}],
    # Use custom_max_token to control max_tokens
    custom_max_token=1000  # This will be used to set max_tokens
)

print(response.choices[0].message.content)
```

**Important Notes**:
- `custom_max_token` **ALWAYS** overrides `max_tokens`, even if both are specified
- If `custom_max_token` is not specified, the handler will use the default value from `CUSTOM_MAX_TOKEN_DEFAULT` environment variable
- Any `max_tokens` value in the request will be replaced by `custom_max_token`

#### Using cURL

```bash
curl http://localhost:4000/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-litellm-key" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello!"}],
    "custom_max_token": 1000
  }'
```

## Custom Handlers

### MaxTokensModifier

Simple handler that reads `custom_max_token` from requests and uses it to set `max_tokens`.

**Configuration:**
- Set default via `CUSTOM_MAX_TOKEN_DEFAULT` environment variable (default: 2048)
- Or modify the default in `custom_handler.py`

**Behavior:**
- Reads `custom_max_token` from request data
- If not provided, uses the configured default value
- **ALWAYS overrides** `max_tokens` with the `custom_max_token` value (takes precedence)
- Even if `max_tokens` is specified in the request, it will be replaced
- Only processes completion requests (ignores embeddings, etc.)

### ConditionalMaxTokensModifier

Advanced handler with conditional logic and model-specific defaults.

**Features:**
- Model-specific default `custom_max_token` values (different for GPT-4, Claude, etc.)
- Reads `custom_max_token` from request or uses model-specific default
- **ALWAYS overrides** any `max_tokens` value in the request
- Caps final value at maximum limit to prevent excessive costs
- Configurable per-model defaults

**Configuration:**
Edit the `model_custom_max_tokens` dictionary in `custom_handler.py`:

```python
self.model_custom_max_tokens = {
    "gpt-4": 4096,
    "gpt-3.5-turbo": 2048,
    "claude-3-opus": 4096,
    # Add more models...
}
```

### Switching Between Handlers

In `proxy_config.yaml`, under `litellm_settings.callbacks`:

```yaml
# Use simple handler
callbacks:
  - custom_callbacks.custom_handler.MaxTokensModifier

# Or use conditional handler
callbacks:
  - custom_callbacks.custom_handler.ConditionalMaxTokensModifier
```

## Customization

### Creating Your Own Handler

You can create custom handlers by extending the `CustomLogger` class:

```python
from litellm.integrations.custom_logger import CustomLogger

class MyCustomHandler(CustomLogger):
    async def async_pre_call_hook(self, user_api_key_dict, cache, data, call_type):
        # Your custom logic here
        if call_type in ["completion", "text_completion"]:
            # Get custom_max_token from request
            custom_max_token = data.pop("custom_max_token", 2048)
            # Apply your custom logic
            data["max_tokens"] = calculate_max_tokens(custom_max_token, data)
        return data
```

### Use Cases

1. **Custom Parameter**: Use `custom_max_token` as an alternative to `max_tokens` for clearer intent
2. **Cost Control**: Cap `custom_max_token` to prevent expensive requests
3. **Model-Specific Defaults**: Set appropriate defaults for different models
4. **User-Based Limits**: Different `custom_max_token` values for different user tiers
5. **Dynamic Adjustment**: Calculate final max_tokens based on custom_max_token and other factors
6. **Compliance**: Ensure requests meet specific requirements

## Troubleshooting

### Handler Not Being Called

- Ensure the handler path in `proxy_config.yaml` is correct
- Check that `custom_handler.py` is in the correct location
- Verify Python can import the module (`python -c "from custom_handler import MaxTokensModifier"`)

### custom_max_token Not Being Applied

- Check the console output for "Applied custom_max_token" logs
- Ensure you're passing `custom_max_token` in your request
- Verify you're making completion requests (not embeddings, etc.)
- Check the `call_type` is being handled in your custom hook

### Environment Variables Not Loading

- Ensure `.env` file exists in the proxy directory
- Check that environment variables are exported before running litellm
- Use `echo $CUSTOM_MAX_TOKEN_DEFAULT` to verify the variable is set

## Advanced Configuration

### Add Authentication

In `proxy_config.yaml`:

```yaml
general_settings:
  master_key: os.environ/LITELLM_MASTER_KEY
  database_url: "postgresql://user:password@localhost/litellm"
```

### Add Logging

```yaml
litellm_settings:
  success_callback: ["langfuse"]
  failure_callback: ["sentry"]
```

### Load Balancing

```yaml
router_settings:
  routing_strategy: simple-shuffle
  num_retries: 3
```

## References

- [LiteLLM Proxy Documentation](https://docs.litellm.ai/docs/proxy/configs)
- [Modify/Reject Incoming Requests](https://docs.litellm.ai/docs/proxy/call_hooks)
- [Custom Callbacks](https://docs.litellm.ai/docs/observability/custom_callback)
- [Building LiteLLM Plugins](https://dev.to/yigit-konur/building-litellm-plugins-with-asyncprecallhook-for-proxy-mode-3lp6)

## License

This implementation is provided as-is for use with LiteLLM proxy.
