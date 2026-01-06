# API Response Format Analysis: Pi Agent & LiteLLM Proxy

This document provides a comprehensive analysis of the expected response formats for Pi Agent and LiteLLM proxy completion APIs.

## Summary

LiteLLM proxy is **OpenAI-compatible** and returns responses in the standard OpenAI Chat Completions format. Since Pi Agent (Inflection AI) is also designed to be OpenAI-compatible, the response format is consistent across all three systems.

---

## 1. Standard Chat Completions Response Format

This is the format used by:
- OpenAI Chat Completions API (`/v1/chat/completions`)
- LiteLLM Proxy (`/chat/completions`)
- Pi Agent (Inflection AI) - OpenAI-compatible

### Non-Streaming Response

```json
{
  "id": "chatcmpl-565d891b-a42e-4c39-8d14-82a1f5208885",
  "object": "chat.completion",
  "created": 1734366691,
  "model": "gpt-4o-2024-08-06",
  "system_fingerprint": "fp_abc123",
  "service_tier": "default",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you today?",
        "tool_calls": null,
        "function_call": null,
        "refusal": null
      },
      "finish_reason": "stop",
      "logprobs": null
    }
  ],
  "usage": {
    "prompt_tokens": 13,
    "completion_tokens": 43,
    "total_tokens": 56
  }
}
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✅ | Unique identifier for the completion |
| `object` | string | ✅ | Always "chat.completion" for non-streaming |
| `created` | integer | ✅ | Unix timestamp of when the completion was created |
| `model` | string | ✅ | The model used to generate the completion |
| `system_fingerprint` | string | ⚠️ | Backend configuration fingerprint (may be null) |
| `service_tier` | string | ❌ | Service level (optional, e.g., "default") |
| `choices` | array | ✅ | Array of completion choices (usually length 1) |
| `usage` | object | ✅ | Token usage statistics |

### Choices Array Structure

Each choice object contains:

```json
{
  "index": 0,
  "message": {
    "role": "assistant",
    "content": "Response text here",
    "tool_calls": null,
    "function_call": null,
    "refusal": null
  },
  "finish_reason": "stop",
  "logprobs": null
}
```

| Field | Type | Description |
|-------|------|-------------|
| `index` | integer | The index of this choice in the array |
| `message` | object | The generated message |
| `message.role` | string | Always "assistant" |
| `message.content` | string | The actual response text (may be null if using tools) |
| `message.tool_calls` | array\|null | Tool/function calls if requested |
| `message.function_call` | object\|null | Deprecated function calling (legacy) |
| `message.refusal` | string\|null | Model's refusal message if it refused |
| `finish_reason` | string | Why generation stopped: "stop", "length", "tool_calls", "content_filter" |
| `logprobs` | object\|null | Log probabilities if requested |

### Usage Object Structure

```json
{
  "prompt_tokens": 13,
  "completion_tokens": 43,
  "total_tokens": 56,
  "completion_tokens_details": {
    "reasoning_tokens": 0
  }
}
```

---

## 2. Streaming Response Format

When `stream: true` is set, the API returns Server-Sent Events (SSE) format.

### Streaming Chunk Structure

```
data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1734366691,"model":"gpt-4","choices":[{"index":0,"delta":{"role":"assistant","content":""},"finish_reason":null}]}

data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1734366691,"model":"gpt-4","choices":[{"index":0,"delta":{"content":"Hello"},"finish_reason":null}]}

data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1734366691,"model":"gpt-4","choices":[{"index":0,"delta":{"content":"!"},"finish_reason":null}]}

data: {"id":"chatcmpl-abc123","object":"chat.completion.chunk","created":1734366691,"model":"gpt-4","choices":[{"index":0,"delta":{},"finish_reason":"stop"}],"usage":{"prompt_tokens":13,"completion_tokens":2,"total_tokens":15}}

data: [DONE]
```

### Key Differences in Streaming:

- `object` is `"chat.completion.chunk"` instead of `"chat.completion"`
- `choices[].delta` is used instead of `choices[].message`
- First chunk typically includes `role` in delta
- Subsequent chunks include incremental `content`
- Final chunk includes `finish_reason` and `usage`
- Stream ends with `data: [DONE]`

---

## 3. LiteLLM Responses API Format

LiteLLM also supports OpenAI's newer **Responses API** format via the `/responses` endpoint.

### Responses API Structure

```json
{
  "id": "resp_abc123",
  "object": "response",
  "created_at": 1734366691,
  "status": "completed",
  "model": "o1-pro-2025-01-30",
  "output": [
    {
      "type": "message",
      "id": "msg_abc123",
      "status": "completed",
      "role": "assistant",
      "content": [
        {
          "type": "output_text",
          "text": "Hello! How can I help you today?",
          "annotations": []
        }
      ]
    }
  ],
  "usage": {
    "input_tokens": 18,
    "output_tokens": 98,
    "total_tokens": 116
  }
}
```

### Key Differences from Chat Completions:

| Aspect | Chat Completions | Responses API |
|--------|------------------|---------------|
| Top-level object | `"chat.completion"` | `"response"` |
| Response field | `choices` array | `output` array |
| Message structure | Flat `message` object | Nested with `type`, `id`, `status` |
| Content field | Direct string | Array with `type` and `text` |
| Timestamp field | `created` | `created_at` |
| Status tracking | Via `finish_reason` | Dedicated `status` field |

---

## 4. Pi Agent (Inflection AI) Specifics

Based on research, Pi Agent API is **OpenAI-compatible** with some variations:

### Model Selection

Pi uses the `config` field for model selection:
- `"inflection_3_pi"` - Pi model (emotional intelligence, customer support)
- `"inflection_3_productivity"` - Productivity model (JSON output, precise guidelines)

### Example Request

```json
{
  "config": "inflection_3_pi",
  "messages": [
    {"role": "user", "content": "Hello!"}
  ],
  "temperature": 0.7
}
```

### Expected Response

Pi returns standard OpenAI format with Pi's response text, completion status, and timestamp.

---

## 5. What Your Proxy Should Return

Your OpenAI-compatible proxy for Pi Agent should return responses in the **standard Chat Completions format** (Section 1).

### Minimum Required Fields:

```json
{
  "id": "chatcmpl-{unique-id}",
  "object": "chat.completion",
  "created": {unix-timestamp},
  "model": "pi",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "{response-text}"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": {count},
    "completion_tokens": {count},
    "total_tokens": {count}
  }
}
```

### For Streaming Responses:

```
data: {"id":"chatcmpl-{id}","object":"chat.completion.chunk","created":{timestamp},"model":"pi","choices":[{"index":0,"delta":{"role":"assistant","content":""},"finish_reason":null}]}

data: {"id":"chatcmpl-{id}","object":"chat.completion.chunk","created":{timestamp},"model":"pi","choices":[{"index":0,"delta":{"content":"Hello"},"finish_reason":null}]}

data: [DONE]
```

---

## 6. Validation Checklist

When implementing your proxy, ensure it returns:

- ✅ Correct `object` type: `"chat.completion"` (non-streaming) or `"chat.completion.chunk"` (streaming)
- ✅ Valid `id` field (unique identifier)
- ✅ Unix `created` timestamp
- ✅ `model` field matching the requested model
- ✅ `choices` array with at least one choice
- ✅ Each choice has `index`, `message`/`delta`, and `finish_reason`
- ✅ `message` object has `role` and `content`
- ✅ `usage` object with token counts
- ✅ Streaming ends with `data: [DONE]`
- ✅ SSE format: each line starts with `data: `

---

## 7. Current Proxy Implementation Status

Your current proxy in `my_proxy/server.py` implements:

✅ Correct non-streaming response format
✅ Correct streaming response format
✅ Proper SSE formatting
✅ Token usage tracking
✅ Model field preservation
✅ OpenAI-compatible endpoints

### Potential Improvements:

1. **Error Response Format**: Ensure errors follow OpenAI format:
```json
{
  "error": {
    "message": "Error description",
    "type": "invalid_request_error",
    "param": null,
    "code": null
  }
}
```

2. **Additional Fields**: Consider adding:
   - `system_fingerprint` (optional but common)
   - `service_tier` (optional)
   - Request parameter echo (for debugging)

3. **Streaming Improvements**:
   - Ensure proper async iteration
   - Handle network interruptions gracefully
   - Add connection timeout handling

---

## References

- [LiteLLM Documentation](https://docs.litellm.ai/docs/)
- [LiteLLM Proxy Server](https://docs.litellm.ai/docs/providers/litellm_proxy)
- [LiteLLM Responses API](https://docs.litellm.ai/docs/response_api)
- [OpenAI Chat Completions](https://platform.openai.com/docs/api-reference/chat)
- [Inflection Pi API](https://www.ai4chat.co/api-chat/inflection-3-pi)
- [OpenAI Responses API Migration](https://platform.openai.com/docs/guides/migrate-to-responses)

---

**Last Updated**: 2026-01-06
