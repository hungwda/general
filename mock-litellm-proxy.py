#!/usr/bin/env python3
"""
Mock LiteLLM Proxy Server with FastAPI
Simulates OpenAI Chat Completions API with streaming and non-streaming support
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Literal
import json
import time
import random
import string
from datetime import datetime
import asyncio
import uvicorn

app = FastAPI(
    title="Mock LiteLLM Proxy",
    description="OpenAI-compatible chat completions API for testing",
    version="1.0.0"
)

# Random text generators
RANDOM_WORDS = [
    "hello", "world", "python", "coding", "agent", "streaming", "data",
    "response", "server", "proxy", "litellm", "openai", "api", "test",
    "random", "text", "generation", "mock", "implementation", "example",
    "fastapi", "async", "performance", "compatible", "format"
]

RANDOM_SENTENCES = [
    "This is a random response from the mock server.",
    "The streaming functionality is working correctly.",
    "Here's some generated text for testing purposes.",
    "LiteLLM proxy compatibility is being tested.",
    "Random text generation helps verify the implementation.",
    "The coding agent should be able to process this response.",
    "Both streaming and non-streaming modes are supported.",
    "This mock server simulates the OpenAI API format.",
    "FastAPI provides excellent async support for streaming.",
    "The response format matches OpenAI specifications."
]

# Pydantic models for request validation
class Message(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    name: Optional[str] = None

class StreamOptions(BaseModel):
    include_usage: bool = False

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    stream: bool = False
    stream_options: Optional[StreamOptions] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None

def generate_random_text(length: int = 50) -> str:
    """Generate random text of specified length"""
    words = []
    current_length = 0
    while current_length < length:
        word = random.choice(RANDOM_WORDS)
        words.append(word)
        current_length += len(word) + 1
    return " ".join(words)

def generate_random_response() -> str:
    """Generate a random sentence or paragraph"""
    if random.random() < 0.5:
        return random.choice(RANDOM_SENTENCES)
    else:
        num_sentences = random.randint(2, 5)
        return " ".join(random.sample(RANDOM_SENTENCES, min(num_sentences, len(RANDOM_SENTENCES))))

async def generate_streaming_response(request_data: ChatCompletionRequest):
    """Generate SSE streaming response"""
    model = request_data.model
    chat_id = f"chatcmpl-{''.join(random.choices(string.ascii_letters + string.digits, k=10))}"
    created = int(datetime.now().timestamp())

    # Generate the full response text
    full_text = generate_random_response()

    # Split into chunks (by words for more realistic streaming)
    words = full_text.split()

    # Initial chunk with role
    initial_chunk = {
        "id": chat_id,
        "object": "chat.completion.chunk",
        "created": created,
        "model": model,
        "choices": [{
            "index": 0,
            "delta": {
                "role": "assistant",
                "content": ""
            },
            "finish_reason": None
        }]
    }
    yield f"data: {json.dumps(initial_chunk)}\n\n"
    await asyncio.sleep(0.05)

    # Stream content word by word
    prompt_tokens = random.randint(10, 50)
    completion_tokens = 0

    for i, word in enumerate(words):
        content = word if i == 0 else f" {word}"
        completion_tokens += 1

        chunk = {
            "id": chat_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": model,
            "choices": [{
                "index": 0,
                "delta": {
                    "content": content
                },
                "finish_reason": None
            }]
        }
        yield f"data: {json.dumps(chunk)}\n\n"

        # Random delay to simulate network latency
        await asyncio.sleep(random.uniform(0.02, 0.1))

    # Final chunk with finish_reason and usage
    total_tokens = prompt_tokens + completion_tokens
    final_chunk = {
        "id": chat_id,
        "object": "chat.completion.chunk",
        "created": created,
        "model": model,
        "choices": [{
            "index": 0,
            "delta": {},
            "finish_reason": "stop"
        }]
    }

    # Include usage if requested
    if request_data.stream_options and request_data.stream_options.include_usage:
        final_chunk["usage"] = {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "prompt_tokens_details": {
                "cached_tokens": random.randint(0, prompt_tokens // 2)
            },
            "completion_tokens_details": {
                "reasoning_tokens": random.randint(0, completion_tokens // 3)
            }
        }

    yield f"data: {json.dumps(final_chunk)}\n\n"
    yield "data: [DONE]\n\n"

def generate_non_streaming_response(request_data: ChatCompletionRequest) -> Dict[str, Any]:
    """Generate non-streaming response"""
    model = request_data.model
    chat_id = f"chatcmpl-{''.join(random.choices(string.ascii_letters + string.digits, k=10))}"
    created = int(datetime.now().timestamp())

    # Generate the full response text
    full_text = generate_random_response()

    # Token counts
    prompt_tokens = random.randint(10, 50)
    completion_tokens = len(full_text.split())
    total_tokens = prompt_tokens + completion_tokens

    response = {
        "id": chat_id,
        "object": "chat.completion",
        "created": created,
        "model": model,
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": full_text
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "prompt_tokens_details": {
                "cached_tokens": random.randint(0, prompt_tokens // 2)
            },
            "completion_tokens_details": {
                "reasoning_tokens": random.randint(0, completion_tokens // 3)
            }
        }
    }

    return response

@app.post("/v1/chat/completions")
async def chat_completions(request_data: ChatCompletionRequest):
    """OpenAI-compatible chat completions endpoint"""
    try:
        if request_data.stream:
            # Return SSE streaming response
            return StreamingResponse(
                generate_streaming_response(request_data),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "X-Accel-Buffering": "no",
                    "Connection": "keep-alive"
                }
            )
        else:
            # Return non-streaming response
            response = generate_non_streaming_response(request_data)
            return JSONResponse(content=response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "mock-litellm-proxy",
        "version": "1.0.0",
        "framework": "fastapi"
    }

@app.get("/")
async def index():
    """Root endpoint with API info"""
    return {
        "service": "Mock LiteLLM Proxy Server (FastAPI)",
        "description": "OpenAI-compatible chat completions API",
        "endpoints": {
            "chat_completions": "/v1/chat/completions",
            "health": "/health",
            "docs": "/docs",
            "openapi": "/openapi.json"
        },
        "features": [
            "Streaming mode (stream: true)",
            "Non-streaming mode (stream: false)",
            "Random text generation",
            "OpenAI API compatible",
            "Async/await support",
            "Auto-generated API docs"
        ]
    }

if __name__ == '__main__':
    print("=" * 60)
    print("Mock LiteLLM Proxy Server (FastAPI)")
    print("=" * 60)
    print("Starting server on http://localhost:8000")
    print("\nEndpoints:")
    print("  - POST /v1/chat/completions (OpenAI compatible)")
    print("  - GET  /health (Health check)")
    print("  - GET  / (API info)")
    print("  - GET  /docs (Interactive API docs)")
    print("\nFeatures:")
    print("  ✓ Streaming mode (stream: true)")
    print("  ✓ Non-streaming mode (stream: false)")
    print("  ✓ Random text generation")
    print("  ✓ Token usage tracking")
    print("  ✓ Async/await support")
    print("  ✓ Pydantic validation")
    print("=" * 60)
    print()

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
