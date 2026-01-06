# Pi Agent OpenAI Proxy

An OpenAI-compatible proxy server for Pi Agent (Inflection AI). This proxy allows you to use Pi with any tool or library that supports the OpenAI API format.

## Features

- ✅ OpenAI-compatible API endpoints
- ✅ Support for streaming and non-streaming responses
- ✅ Chat completions endpoint (`/v1/chat/completions`)
- ✅ Model listing endpoint (`/v1/models`)
- ✅ Easy integration with existing OpenAI client libraries

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your Pi API key:
```bash
export PI_API_KEY="your-pi-api-key-here"
```

Optionally, set a custom Pi API URL:
```bash
export PI_API_URL="https://api.inflection.ai/v1/chat/completions"
```

## Usage

### Starting the Server

```bash
python server.py
```

The server will start on `http://localhost:8000` by default. You can change the port:

```bash
PORT=8080 python server.py
```

### Using with OpenAI Python Client

```python
from openai import OpenAI

# Point the client to your proxy server
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy-key"  # Not used, but required by the client
)

# Use it like normal OpenAI API
response = client.chat.completions.create(
    model="pi",
    messages=[
        {"role": "user", "content": "Hello, how are you?"}
    ]
)

print(response.choices[0].message.content)
```

### Streaming Example

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy-key"
)

stream = client.chat.completions.create(
    model="pi",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### Using with curl

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "pi",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## API Endpoints

### `POST /v1/chat/completions`

OpenAI-compatible chat completions endpoint.

**Request Body:**
```json
{
  "model": "pi",
  "messages": [
    {"role": "user", "content": "Hello!"}
  ],
  "temperature": 0.7,
  "max_tokens": 1000,
  "stream": false
}
```

**Response:**
```json
{
  "id": "chatcmpl-...",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "pi",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you today?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

### `GET /v1/models`

List available models.

### `GET /health`

Health check endpoint.

## Environment Variables

- `PI_API_KEY` (required): Your Pi API key
- `PI_API_URL` (optional): Pi API endpoint (default: `https://api.inflection.ai/v1/chat/completions`)
- `PORT` (optional): Server port (default: `8000`)

## Docker Support

Create a `.env` file:
```
PI_API_KEY=your-api-key-here
```

Run with Docker:
```bash
docker build -t pi-proxy .
docker run -p 8000:8000 --env-file .env pi-proxy
```

## Notes

- The proxy translates between OpenAI's API format and Pi's API format
- You need a valid Pi API key from Inflection AI
- This is a development server - for production use, deploy with a proper ASGI server like Gunicorn

## License

MIT
