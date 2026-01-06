# Mock LiteLLM Proxy Server (FastAPI)

A simple Python server that simulates the LiteLLM proxy with OpenAI Chat Completions API compatibility. Supports both streaming and non-streaming modes with random text generation.

## Features

- ✅ **OpenAI Chat Completions API compatible**
- ✅ **Streaming mode** (Server-Sent Events)
- ✅ **Non-streaming mode** (JSON response)
- ✅ **Random text generation** for testing
- ✅ **Token usage tracking** (including cached and reasoning tokens)
- ✅ **Realistic streaming delays** to simulate network latency
- ✅ **FastAPI with async/await** for better performance
- ✅ **Pydantic validation** for request data
- ✅ **Auto-generated API docs** (Swagger UI)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Start the Server

```bash
python mock-litellm-proxy.py
```

Or using uvicorn directly:
```bash
uvicorn mock-litellm-proxy:app --host 0.0.0.0 --port 8000 --reload
```

Server will start on `http://localhost:8000`

### Test the Server

Make the test script executable and run it:
```bash
chmod +x test-proxy.sh
./test-proxy.sh
```

### View API Documentation

FastAPI provides auto-generated interactive API docs:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## API Endpoints

### POST /v1/chat/completions

OpenAI-compatible chat completions endpoint.

#### Non-Streaming Request

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-test-key" \
  -d '{
    "model": "gpt-4",
    "messages": [
      {"role": "user", "content": "Hello"}
    ],
    "stream": false
  }'
```

Response:
```json
{
  "id": "chatcmpl-abc123",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "gpt-4",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "This is a random response from the mock server."
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 25,
    "completion_tokens": 10,
    "total_tokens": 35,
    "prompt_tokens_details": {
      "cached_tokens": 5
    },
    "completion_tokens_details": {
      "reasoning_tokens": 2
    }
  }
}
```

#### Streaming Request

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-test-key" \
  -d '{
    "model": "gpt-4",
    "messages": [
      {"role": "user", "content": "Hello"}
    ],
    "stream": true,
    "stream_options": {"include_usage": true}
  }'
```

Response (SSE format):
```
data: {"id":"chatcmpl-xyz","object":"chat.completion.chunk","created":1234567890,"model":"gpt-4","choices":[{"index":0,"delta":{"role":"assistant","content":""},"finish_reason":null}]}

data: {"id":"chatcmpl-xyz","object":"chat.completion.chunk","created":1234567890,"model":"gpt-4","choices":[{"index":0,"delta":{"content":"This"},"finish_reason":null}]}

data: {"id":"chatcmpl-xyz","object":"chat.completion.chunk","created":1234567890,"model":"gpt-4","choices":[{"index":0,"delta":{"content":" is"},"finish_reason":null}]}

...

data: {"id":"chatcmpl-xyz","object":"chat.completion.chunk","created":1234567890,"model":"gpt-4","choices":[{"index":0,"delta":{},"finish_reason":"stop"}],"usage":{"prompt_tokens":25,"completion_tokens":10,"total_tokens":35}}

data: [DONE]
```

### GET /health

Health check endpoint.

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "ok",
  "service": "mock-litellm-proxy",
  "version": "1.0.0",
  "framework": "fastapi"
}
```

### GET /

API information endpoint.

```bash
curl http://localhost:8000/
```

### GET /docs

Interactive Swagger UI documentation (browser only).

### GET /redoc

Alternative ReDoc documentation (browser only).

## Using with Pi Coding Agent

Configure the coding agent to use this mock proxy by creating a `models.json`:

```json
{
  "providers": {
    "mock-litellm": {
      "baseUrl": "http://localhost:8000/v1",
      "apiKey": "sk-test-key",
      "api": "openai-completions",
      "models": [
        {
          "id": "mock-model",
          "name": "Mock Model for Testing",
          "reasoning": false,
          "input": ["text"],
          "cost": {
            "input": 0,
            "output": 0,
            "cacheRead": 0,
            "cacheWrite": 0
          },
          "contextWindow": 32000,
          "maxTokens": 4096
        }
      ]
    }
  }
}
```

## Request Schema

The server validates requests using Pydantic models:

```python
class ChatCompletionRequest(BaseModel):
    model: str                              # Required
    messages: List[Message]                 # Required
    stream: bool = False                    # Optional
    stream_options: Optional[StreamOptions] # Optional
    temperature: Optional[float]            # Optional
    max_tokens: Optional[int]              # Optional
    top_p: Optional[float]                 # Optional

class Message(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    name: Optional[str] = None

class StreamOptions(BaseModel):
    include_usage: bool = False
```

## Response Format

The server follows the OpenAI Chat Completions API specification:

- **Streaming**: Server-Sent Events (SSE) with `ChatCompletionChunk` objects
- **Non-Streaming**: Standard `ChatCompletion` JSON response
- **Token Tracking**: Includes prompt tokens, completion tokens, cached tokens, and reasoning tokens
- **Finish Reasons**: Currently only returns `"stop"` but can be extended

## Customization

### Add Custom Responses

Edit the `RANDOM_SENTENCES` list in `mock-litellm-proxy.py`:

```python
RANDOM_SENTENCES = [
    "Your custom response here",
    "Another custom response",
    # Add more...
]
```

### Adjust Streaming Delay

Modify the sleep time in `generate_streaming_response()`:

```python
await asyncio.sleep(random.uniform(0.02, 0.1))  # Adjust these values
```

### Change Server Port

Modify the uvicorn configuration:

```python
uvicorn.run(app, host="0.0.0.0", port=9000)  # Change port here
```

Or run directly:
```bash
uvicorn mock-litellm-proxy:app --port 9000
```

## FastAPI Advantages

- **Async/Await**: Native async support for better performance
- **Type Safety**: Pydantic models provide automatic validation
- **Auto Documentation**: Swagger UI and ReDoc generated automatically
- **Performance**: Faster than Flask for async operations
- **Modern**: Built on modern Python standards (type hints, async)

## Production Deployment

For production use:

```bash
# With multiple workers
uvicorn mock-litellm-proxy:app --host 0.0.0.0 --port 8000 --workers 4

# With Gunicorn (production-ready)
gunicorn mock-litellm-proxy:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Testing

### Manual Test with curl

```bash
# Test health
curl http://localhost:8000/health

# Test non-streaming
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"test","messages":[{"role":"user","content":"hi"}]}'

# Test streaming
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"test","messages":[{"role":"user","content":"hi"}],"stream":true,"stream_options":{"include_usage":true}}'
```

### With Python OpenAI SDK

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="sk-test-key"
)

# Non-streaming
response = client.chat.completions.create(
    model="test",
    messages=[{"role": "user", "content": "Hello"}]
)
print(response.choices[0].message.content)

# Streaming
stream = client.chat.completions.create(
    model="test",
    messages=[{"role": "user", "content": "Hello"}],
    stream=True
)
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

## Limitations

- No actual AI model - returns random text
- No conversation history tracking
- No tool/function calling support (yet)
- Single model support (can be extended)
- No authentication validation

## Future Enhancements

Potential additions:
- Tool/function calling support
- Multiple model simulation
- Conversation state tracking
- Rate limiting
- Authentication/API key validation
- Error simulation modes
- Configurable response templates

## License

This is a testing tool - use freely for development and testing purposes.
