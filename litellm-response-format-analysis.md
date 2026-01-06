# LiteLLM Proxy Response Format Analysis for Pi Coding Agent

## Summary

The Pi Coding Agent expects **OpenAI Chat Completions API compatible responses** from the LiteLLM proxy. It works with **both streaming and non-streaming** modes, using the standard OpenAI SDK response format.

---

## API Configuration

The coding agent uses the `openai-completions` API type for LiteLLM proxies. Configuration example:

```json
{
  "providers": {
    "litellm": {
      "baseUrl": "http://localhost:8000/v1",
      "apiKey": "sk-litellm-key",
      "api": "openai-completions",
      "models": [...]
    }
  }
}
```

**Source:** `/tmp/pi-mono/packages/coding-agent/src/core/model-registry.ts:384`

---

## Response Format Details

### 1. Streaming Mode (Primary Mode)

The agent **always uses streaming** by default, calling the OpenAI SDK with:

```typescript
{
  model: model.id,
  messages: [...],
  stream: true,
  stream_options: { include_usage: true }
}
```

**Source:** `/tmp/pi-mono/packages/ai/src/providers/openai-completions.ts:366-371`

#### Expected Streaming Response Format

LiteLLM must return **Server-Sent Events (SSE)** with `ChatCompletionChunk` objects:

```typescript
// Each SSE event contains a chunk like this:
interface ChatCompletionChunk {
  id: string;
  object: "chat.completion.chunk";
  created: number;
  model: string;
  choices: [
    {
      index: 0;
      delta: {
        // Text content (streamed incrementally)
        content?: string;

        // Tool calls (streamed incrementally)
        tool_calls?: Array<{
          index: number;
          id?: string;
          type?: "function";
          function?: {
            name?: string;
            arguments?: string; // Partial JSON string
          };
        }>;

        // Reasoning/thinking content (various field names supported)
        reasoning_content?: string;  // llama.cpp format
        reasoning?: string;           // Generic format
        reasoning_text?: string;      // Alternative format

        // Encrypted reasoning details (for advanced models)
        reasoning_details?: Array<{
          type: "reasoning.encrypted";
          id: string;
          data: any;
        }>;
      };

      // Finish reason (only in final chunk)
      finish_reason?: "stop" | "length" | "tool_calls" | "content_filter" | null;
    }
  ];

  // Usage information (sent in final chunk when stream_options.include_usage = true)
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
    prompt_tokens_details?: {
      cached_tokens?: number;
    };
    completion_tokens_details?: {
      reasoning_tokens?: number;
    };
  };
}
```

**Source:** `/tmp/pi-mono/packages/ai/src/providers/openai-completions.ts:140-292`

#### How the Agent Processes Streaming Chunks

The agent processes each chunk and emits internal events:

1. **Text Streaming** (lines 174-195):
   - Detects `delta.content` field
   - Emits: `text_start` → `text_delta` (multiple) → `text_end`

2. **Reasoning/Thinking Streaming** (lines 197-238):
   - Checks multiple field names: `reasoning_content`, `reasoning`, `reasoning_text`
   - Uses first non-empty field to avoid duplication
   - Emits: `thinking_start` → `thinking_delta` (multiple) → `thinking_end`

3. **Tool Call Streaming** (lines 240-276):
   - Processes `delta.tool_calls` array
   - Accumulates partial JSON arguments
   - Emits: `toolcall_start` → `toolcall_delta` (multiple) → `toolcall_end`

4. **Usage Information** (lines 141-164):
   - Extracts from `chunk.usage` in final chunk
   - Calculates: input tokens (excluding cached), output tokens (including reasoning), cache reads
   - Computes cost based on model pricing

5. **Finish Reason** (lines 169-171):
   - Maps OpenAI finish reasons to internal stop reasons
   - `stop` → "stop", `length` → "length", `tool_calls`/`function_call` → "toolUse"

---

### 2. Non-Streaming Mode

While streaming is the default, non-streaming is supported via the `complete()` function which internally calls `stream().result()`.

**Source:** `/tmp/pi-mono/packages/ai/src/stream.ts:132-139`

#### Expected Non-Streaming Response Format

For non-streaming, LiteLLM should return a standard OpenAI `ChatCompletion` object:

```typescript
interface ChatCompletion {
  id: string;
  object: "chat.completion";
  created: number;
  model: string;
  choices: [
    {
      index: 0;
      message: {
        role: "assistant";
        content: string | null;
        tool_calls?: Array<{
          id: string;
          type: "function";
          function: {
            name: string;
            arguments: string; // Complete JSON string
          };
        }>;
        // Reasoning fields (if supported by model)
        reasoning_content?: string;
        reasoning?: string;
      };
      finish_reason: "stop" | "length" | "tool_calls" | "content_filter";
    }
  ];
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
    prompt_tokens_details?: {
      cached_tokens?: number;
    };
    completion_tokens_details?: {
      reasoning_tokens?: number;
    };
  };
}
```

However, in practice, the agent **always uses streaming mode**, so non-streaming is rarely used.

---

## Supported Features

### ✅ Fully Supported

1. **Text Generation**: Standard assistant responses
2. **Tool/Function Calling**: OpenAI-style tool calls with streaming support
3. **Reasoning/Thinking Tokens**: Multiple field name formats supported
4. **Token Usage & Costs**: Detailed tracking including cached and reasoning tokens
5. **Streaming**: Primary mode of operation
6. **Stop Reasons**: All standard OpenAI finish reasons

### ⚠️ Compatibility Settings

The agent auto-detects provider quirks based on `baseUrl` but also supports explicit configuration:

**Source:** `/tmp/pi-mono/packages/ai/src/providers/openai-completions.ts:641-685`

```json
{
  "compat": {
    "supportsStore": false,              // Whether to include 'store' field
    "supportsDeveloperRole": true,       // Use 'developer' vs 'system' role
    "supportsReasoningEffort": false,    // Support 'reasoning_effort' param
    "maxTokensField": "max_tokens",      // Use 'max_tokens' vs 'max_completion_tokens'
    "requiresToolResultName": false,     // Require 'name' in tool results
    "requiresAssistantAfterToolResult": false,  // Insert assistant message after tools
    "requiresThinkingAsText": false,     // Convert thinking to text with <thinking> tags
    "requiresMistralToolIds": false      // Normalize tool IDs to 9 alphanumeric chars
  }
}
```

---

## Request Format Sent by Agent

### Request Parameters

```typescript
{
  model: "model-id",
  messages: ChatCompletionMessageParam[],
  stream: true,
  stream_options: { include_usage: true },

  // Optional based on context
  store?: false,
  max_completion_tokens?: number,      // or max_tokens depending on compat
  temperature?: number,
  tools?: Array<{
    type: "function",
    function: {
      name: string,
      description: string,
      parameters: object  // JSON Schema
    }
  }>,
  tool_choice?: "auto" | "none" | "required" | { type: "function", function: { name: string } },
  reasoning_effort?: "minimal" | "low" | "medium" | "high" | "xhigh"
}
```

**Source:** `/tmp/pi-mono/packages/ai/src/providers/openai-completions.ts:362-405`

### Message Conversion

The agent converts its internal message format to OpenAI format:

**Source:** `/tmp/pi-mono/packages/ai/src/providers/openai-completions.ts:407-605`

1. **System Prompt** → `system` role (or `developer` for reasoning models)
2. **User Messages** → `user` role with text/image content
3. **Assistant Messages** → `assistant` role with text/tool_calls
4. **Tool Results** → `tool` role with content and tool_call_id

Special handling:
- Images encoded as base64 data URLs: `data:image/jpeg;base64,...`
- Mistral compatibility: Tool IDs normalized to 9 alphanumeric characters
- Empty assistant messages are skipped (Mistral requirement)

---

## Event Stream Architecture

The agent uses an event-driven architecture for streaming:

**Source:** `/tmp/pi-mono/packages/ai/src/utils/event-stream.ts:68-82`

### Event Types Emitted

```typescript
type AssistantMessageEvent =
  | { type: "start"; partial: AssistantMessage }
  | { type: "text_start"; contentIndex: number; partial: AssistantMessage }
  | { type: "text_delta"; contentIndex: number; delta: string; partial: AssistantMessage }
  | { type: "text_end"; contentIndex: number; content: string; partial: AssistantMessage }
  | { type: "thinking_start"; contentIndex: number; partial: AssistantMessage }
  | { type: "thinking_delta"; contentIndex: number; delta: string; partial: AssistantMessage }
  | { type: "thinking_end"; contentIndex: number; content: string; partial: AssistantMessage }
  | { type: "toolcall_start"; contentIndex: number; partial: AssistantMessage }
  | { type: "toolcall_delta"; contentIndex: number; delta: string; partial: AssistantMessage }
  | { type: "toolcall_end"; contentIndex: number; toolCall: ToolCall; partial: AssistantMessage }
  | { type: "done"; reason: "stop" | "length" | "toolUse"; message: AssistantMessage }
  | { type: "error"; reason: "aborted" | "error"; error: AssistantMessage };
```

**Source:** `/tmp/pi-mono/packages/ai/src/types.ts:168-180`

These events are consumed by:
- Interactive terminal UI for real-time rendering
- RPC mode for JSON protocol communication
- Session management for persistence

---

## Key Implementation Details

### 1. Partial JSON Parsing for Tool Arguments

**Source:** `/tmp/pi-mono/packages/ai/src/providers/openai-completions.ts:263-267`

The agent uses `parseStreamingJson()` to handle incomplete JSON in tool call arguments during streaming, allowing it to display partial tool parameters in real-time.

### 2. Reasoning Token Handling

**Source:** `/tmp/pi-mono/packages/ai/src/providers/openai-completions.ts:143-145`

Reasoning tokens are **added to output tokens** (not input), and the agent recalculates `totalTokens` because some providers (like Groq) don't include reasoning tokens in their reported total.

### 3. Multiple Reasoning Field Support

**Source:** `/tmp/pi-mono/packages/ai/src/providers/openai-completions.ts:197-214`

The agent checks multiple field names for reasoning content to support different provider conventions:
- `reasoning_content` (llama.cpp)
- `reasoning` (generic)
- `reasoning_text` (alternative)

It uses the **first non-empty field** to avoid duplication when providers return the same content in multiple fields.

### 4. Unicode Sanitization

**Source:** `/tmp/pi-mono/packages/ai/src/providers/openai-completions.ts:419`

All text content is passed through `sanitizeSurrogates()` to handle invalid Unicode surrogate pairs that could crash the terminal or cause rendering issues.

---

## Testing Your LiteLLM Proxy

### Minimal Working Example

Your LiteLLM proxy should respond to this request:

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-litellm-key" \
  -d '{
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "Hello"}],
    "stream": true,
    "stream_options": {"include_usage": true}
  }'
```

Expected response (SSE format):

```
data: {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1234567890,"model":"gpt-4","choices":[{"index":0,"delta":{"role":"assistant","content":""},"finish_reason":null}]}

data: {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1234567890,"model":"gpt-4","choices":[{"index":0,"delta":{"content":"Hello"},"finish_reason":null}]}

data: {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1234567890,"model":"gpt-4","choices":[{"index":0,"delta":{"content":"!"},"finish_reason":null}]}

data: {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1234567890,"model":"gpt-4","choices":[{"index":0,"delta":{},"finish_reason":"stop"}],"usage":{"prompt_tokens":10,"completion_tokens":2,"total_tokens":12}}

data: [DONE]
```

### Tool Calling Example

For tool calls, the streaming chunks should look like:

```
data: {"choices":[{"delta":{"tool_calls":[{"index":0,"id":"call_abc123","type":"function","function":{"name":"get_weather"}}]}}]}

data: {"choices":[{"delta":{"tool_calls":[{"index":0,"function":{"arguments":"{\"loc"}}]}}]}

data: {"choices":[{"delta":{"tool_calls":[{"index":0,"function":{"arguments":"ation\":"}}]}}]}

data: {"choices":[{"delta":{"tool_calls":[{"index":0,"function":{"arguments":"\"NYC\"}"}}]}}]}

data: {"choices":[{"delta":{},"finish_reason":"tool_calls"}],"usage":{...}}
```

### Reasoning Token Example

For models with reasoning capabilities:

```
data: {"choices":[{"delta":{"reasoning_content":"Let me think..."}}]}

data: {"choices":[{"delta":{"reasoning_content":" about this."}}]}

data: {"choices":[{"delta":{"content":"Based on my reasoning, "}}]}

data: {"choices":[{"delta":{"content":"the answer is 42."}}]}

data: {"choices":[{"delta":{},"finish_reason":"stop"}],"usage":{"prompt_tokens":10,"completion_tokens":8,"total_tokens":18,"completion_tokens_details":{"reasoning_tokens":5}}}
```

---

## Conclusion

### Both Streaming and Non-Streaming Work: ✅

- **Streaming**: Primary mode, fully supported with real-time event processing
- **Non-streaming**: Supported but rarely used (internally converts to streaming)

### Required for LiteLLM Compatibility:

1. ✅ Implement OpenAI Chat Completions API format
2. ✅ Support SSE streaming with `stream: true`
3. ✅ Include usage information in final chunk with `stream_options.include_usage`
4. ✅ Send `delta` objects with incremental content
5. ✅ Properly format tool calls with streaming support
6. ✅ (Optional) Support reasoning tokens in `reasoning_content`/`reasoning` fields

The Pi Coding Agent is **fully compatible** with standard LiteLLM proxy implementations that follow the OpenAI Chat Completions API specification.
