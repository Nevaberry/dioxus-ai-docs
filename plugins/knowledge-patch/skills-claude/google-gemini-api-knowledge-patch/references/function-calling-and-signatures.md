# Function Calling and Thought Signatures

## Preserve opaque signatures in manual history

Thought signatures are encrypted reasoning state attached to response parts.
Official SDKs preserve them when the complete response object is appended to
history. REST clients and applications that construct history manually must
return each signature unchanged on the exact model part where it arrived.

```json
{
  "role": "model",
  "parts": [{
    "functionCall": {"name": "check_flight", "args": {"flight": "AA100"}},
    "thoughtSignature": "<opaque signature>"
  }]
}
```

For Gemini 3.x function calling, including minimal thinking, this round trip is
mandatory. Omitting a required signature returns HTTP 400.

## Retain every signed call in the current turn

Validation scans backward to the newest user message with ordinary content. A
user message containing only a `functionResponse` does not begin a new turn.
Every step after that boundary must retain the signature on its first function
call, so a sequential loop resends all earlier signed model-call parts:

```text
user(text) -> model(FC1 + signature A) -> user(FR1)
           -> model(FC2 + signature B) -> user(FR2)
```

## Keep parallel calls grouped

When one response contains parallel calls, only the first `functionCall` part
carries the signature. Keep it on that part and return all calls in one model
message followed by all results in one user message:

```text
model: [FC1 + signature, FC2]
user:  [FR1, FR2]
```

Interleaving `FC1, FR1, FC2, FR2` fails validation.

## Preserve compatibility-envelope signatures

Chat-completion compatibility responses put the signature on the signed tool
call at `extra_content.google.thought_signature`. Replay the assistant
tool-call message with this extension intact:

```json
{
  "tool_calls": [{
    "extra_content": {
      "google": {"thought_signature": "<opaque signature>"}
    },
    "function": {
      "name": "check_flight",
      "arguments": "{\"flight\":\"AA100\"}"
    }
  }]
}
```

## Consume non-call and streamed signatures

Without a function call, Gemini 3.x may attach a signature to the last content
part. Returning it is recommended for reasoning continuity but is not
validated. In a streamed non-call response it can arrive on a part whose text
is empty, so consume the stream through `finish_reason` rather than stopping
when text is empty.

With function calls, Gemini 2.5 can put an optional signature on the first part
regardless of its type; Gemini 3.x signs the first function-call part and
requires it on replay. Without calls, 2.5 returns no signature, while 3.x can
sign its last part after generating a thought.

## Import unsigned traces only when unavoidable

Do not fabricate function-call blocks when a real API response is available.
When importing a trace that cannot contain genuine signatures, either
documented sentinel can bypass validation in the signature field:

```json
{"thoughtSignature": "context_engineering_is_the_way_to_go"}
```

```json
{"thoughtSignature": "skip_thought_signature_validator"}
```

## Declare Interactions functions directly

Custom functions are typed entries in the Interactions `tools` array; do not
wrap them in a function-declarations container. `parameters` is an object
schema with `properties` and `required`:

```python
weather_tool = {
    "type": "function",
    "name": "get_weather",
    "description": "Get weather for a city.",
    "parameters": {
        "type": "object",
        "properties": {"city": {"type": "string"}},
        "required": ["city"],
    },
}
```

## Control tool selection and validation

Set behavior through `generation_config.tool_choice`: `auto` is the default,
`any` forces a call, `none` prohibits calls, and preview mode `validated`
enforces schema adherence. Restrict callable functions with nested
`allowed_tools`:

```python
generation_config = {
    "tool_choice": {
        "allowed_tools": {"mode": "any", "tools": ["get_weather"]}
    }
}
```

Very large or deeply nested schemas can be rejected in `any` mode.

## Return multimodal function results

For 3-series Interactions, a `function_result` can contain multiple typed
blocks, including images. Preserve the function name and call ID:

```python
input=[{
    "type": "function_result",
    "name": tool_call.name,
    "call_id": tool_call.id,
    "result": [
        {"type": "text", "text": "instrument.jpg"},
        {"type": "image", "mime_type": "image/jpeg", "data": base64_data},
    ],
}]
```

When using legacy `generateContent` with Gemini 3.x, every
`FunctionResponse` likewise includes both its `call_id` and function name.

## Connect remote MCP servers

Interactions accepts an `mcp_server` tool for a remote MCP endpoint. It
supports Streamable HTTP, not SSE. Server names cannot contain hyphens;
`headers` and `allowed_tools` provide authentication and filtering.

```python
tools=[{
    "type": "mcp_server",
    "name": "weather_service",
    "url": "https://example.com/mcp",
    "allowed_tools": ["get_weather"],
}]
```

## Assemble streamed arguments by event index

On the SSE wire, function arguments arrive as partial argument-delta payloads.
SDKs can normalize their names; the Python surface exposes an `arguments`
delta with `partial_arguments`. Capture ID and name at `step.start`, group by
`event.index`, concatenate fragments, and parse only after completion:

```python
if event.event_type == "step.delta" and event.delta.type == "arguments":
    current_calls[event.index]["arguments"] += event.delta.partial_arguments
```

## Avoid rigid structured prose before a tool call

Requiring XML, YAML, or JSON text immediately before a tool call can produce
`Malformed_Function_Call`. Prefer a dedicated function for working notes made
alongside the real call. Markdown notes or removing the pre-tool requirement
are fallbacks.

```json
{
  "name": "update",
  "description": "Record working notes before another tool call.",
  "parameters": {
    "type": "OBJECT",
    "properties": {"next_step": {"type": "STRING"}},
    "required": ["next_step"]
  }
}
```

Batch attribution: `gemini-3-thought-signatures`, `function-calling`, and
`gemini-3.6`.
