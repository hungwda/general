# LiteLLM Proxy with Max Tokens Modifier

This solution provides a custom LiteLLM proxy setup that allows you to replace/modify the `max_tokens` parameter in requests before they are sent to LLM providers.

## Overview

The solution uses LiteLLM's custom callback system with the `async_pre_call_hook` to intercept and modify requests before they reach the LLM provider. This allows you to:

- Override `max_tokens` for all requests
- Set different `max_tokens` based on the model
- Cap `max_tokens` to prevent excessive costs
- Conditionally modify requests based on user, model, or other criteria

## Files

- **custom_handler.py**: Contains custom callback handlers for modifying max_tokens
  - `MaxTokensModifier`: Simple handler that replaces max_tokens with a configured value
  - `ConditionalMaxTokensModifier`: Advanced handler with model-specific and conditional logic
- **proxy_config.yaml**: LiteLLM proxy configuration file
- **requirements.txt**: Python dependencies
- **.env.example**: Example environment variables configuration
- **start_proxy.sh**: Shell script to start the proxy server

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
MAX_TOKENS_OVERRIDE=2048
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
export MAX_TOKENS_OVERRIDE=2048
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
    # max_tokens will be replaced by the custom handler
    max_tokens=1000  # This will be overridden to MAX_TOKENS_OVERRIDE value
)

print(response.choices[0].message.content)
```

#### Using cURL

```bash
curl http://localhost:4000/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-litellm-key" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 1000
  }'
```

## Custom Handlers

### MaxTokensModifier

Simple handler that replaces all `max_tokens` values with a configured value.

**Configuration:**
- Set via `MAX_TOKENS_OVERRIDE` environment variable (default: 2048)
- Or modify the default in `custom_handler.py`

**Behavior:**
- Replaces `max_tokens` for all completion requests
- Ignores embeddings and other request types

### ConditionalMaxTokensModifier

Advanced handler with conditional logic.

**Features:**
- Model-specific max_tokens (different values for GPT-4, Claude, etc.)
- Respects original max_tokens if set, but caps at a maximum limit
- Configurable per-model limits

**Configuration:**
Edit the `model_max_tokens` dictionary in `custom_handler.py`:

```python
self.model_max_tokens = {
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
            # Modify data["max_tokens"] based on your requirements
            data["max_tokens"] = calculate_max_tokens(data)
        return data
```

### Use Cases

1. **Cost Control**: Cap max_tokens to prevent expensive requests
2. **Model-Specific Limits**: Set appropriate limits for different models
3. **User-Based Limits**: Different max_tokens for different user tiers
4. **Dynamic Adjustment**: Calculate max_tokens based on input length
5. **Compliance**: Ensure requests meet specific requirements

## Troubleshooting

### Handler Not Being Called

- Ensure the handler path in `proxy_config.yaml` is correct
- Check that `custom_handler.py` is in the correct location
- Verify Python can import the module (`python -c "from custom_handler import MaxTokensModifier"`)

### Max Tokens Not Being Modified

- Check the console output for "Modified max_tokens" logs
- Ensure you're making completion requests (not embeddings, etc.)
- Verify the `call_type` is being handled in your custom hook

### Environment Variables Not Loading

- Ensure `.env` file exists in the proxy directory
- Check that environment variables are exported before running litellm
- Use `echo $MAX_TOKENS_OVERRIDE` to verify the variable is set

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
