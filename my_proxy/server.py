#!/usr/bin/env python3
"""
OpenAI-compatible proxy server for Pi Agent (Inflection AI)
"""
import os
import json
import asyncio
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
import httpx
import uvicorn
from datetime import datetime

app = FastAPI(title="Pi Agent Proxy", description="OpenAI-compatible proxy for Pi Agent")

# Pi API endpoint
PI_API_URL = os.getenv("PI_API_URL", "https://api.inflection.ai/v1/chat/completions")
PI_API_KEY = os.getenv("PI_API_KEY", "")

class Message(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str = "pi"
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000
    stream: Optional[bool] = False
    top_p: Optional[float] = 1.0
    frequency_penalty: Optional[float] = 0.0
    presence_penalty: Optional[float] = 0.0

def convert_to_pi_format(request: ChatCompletionRequest) -> Dict[str, Any]:
    """Convert OpenAI format to Pi format"""
    return {
        "messages": [{"role": msg.role, "content": msg.content} for msg in request.messages],
        "temperature": request.temperature,
        "max_tokens": request.max_tokens,
        "stream": request.stream,
    }

def convert_from_pi_format(pi_response: Dict[str, Any], model: str = "pi") -> Dict[str, Any]:
    """Convert Pi format to OpenAI format"""
    return {
        "id": pi_response.get("id", f"chatcmpl-{datetime.now().timestamp()}"),
        "object": "chat.completion",
        "created": int(datetime.now().timestamp()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": pi_response.get("choices", [{}])[0].get("message", {}).get("content", "")
                },
                "finish_reason": pi_response.get("choices", [{}])[0].get("finish_reason", "stop")
            }
        ],
        "usage": pi_response.get("usage", {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        })
    }

async def stream_pi_response(response):
    """Stream Pi response in OpenAI format"""
    async for chunk in response.aiter_lines():
        if chunk:
            if chunk.startswith("data: "):
                chunk = chunk[6:]
            if chunk == "[DONE]":
                yield f"data: [DONE]\n\n"
                break

            try:
                data = json.loads(chunk)
                # Convert to OpenAI streaming format
                openai_chunk = {
                    "id": data.get("id", f"chatcmpl-{datetime.now().timestamp()}"),
                    "object": "chat.completion.chunk",
                    "created": int(datetime.now().timestamp()),
                    "model": "pi",
                    "choices": [
                        {
                            "index": 0,
                            "delta": data.get("choices", [{}])[0].get("delta", {}),
                            "finish_reason": data.get("choices", [{}])[0].get("finish_reason")
                        }
                    ]
                }
                yield f"data: {json.dumps(openai_chunk)}\n\n"
            except json.JSONDecodeError:
                continue

@app.get("/")
async def root():
    return {"message": "Pi Agent Proxy Server", "status": "running"}

@app.get("/v1/models")
async def list_models():
    """List available models"""
    return {
        "object": "list",
        "data": [
            {
                "id": "pi",
                "object": "model",
                "created": int(datetime.now().timestamp()),
                "owned_by": "inflection-ai"
            }
        ]
    }

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """OpenAI-compatible chat completions endpoint"""

    if not PI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="PI_API_KEY environment variable not set"
        )

    headers = {
        "Authorization": f"Bearer {PI_API_KEY}",
        "Content-Type": "application/json"
    }

    pi_request = convert_to_pi_format(request)

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            if request.stream:
                # Streaming response
                response = await client.post(
                    PI_API_URL,
                    json=pi_request,
                    headers=headers,
                    timeout=60.0
                )

                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Pi API error: {response.text}"
                    )

                return StreamingResponse(
                    stream_pi_response(response),
                    media_type="text/event-stream"
                )
            else:
                # Non-streaming response
                response = await client.post(
                    PI_API_URL,
                    json=pi_request,
                    headers=headers
                )

                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Pi API error: {response.text}"
                    )

                pi_response = response.json()
                openai_response = convert_from_pi_format(pi_response, request.model)
                return JSONResponse(content=openai_response)

    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Error connecting to Pi API: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
