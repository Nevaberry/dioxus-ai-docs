# Function calling and tools

## Declare Interactions functions directly

Custom functions are direct typed entries in the Interactions `tools` array,
not a wrapper containing a declarations list. `parameters` is an object schema
with `properties` and `required`.

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
interaction = client.interactions.create(
    model="MODEL_ID", input="Weather in Paris?", tools=[weather_tool]
)
```

## Select tool behavior and validate schemas

Set behavior with `generation_config.tool_choice`: `auto` is the default,
`any` forces a call, `none` prohibits calls, and preview `validated` enforces
schema adherence. Restrict callable functions through nested `allowed_tools`.
Forced `any` mode may reject very large or deeply nested schemas.

```python
generation_config = {
    "tool_choice": {
        "allowed_tools": {"mode": "any", "tools": ["get_weather"]}
    }
}
```

## Return multimodal function results

For Gemini 3-series models, an Interactions `function_result` can contain
multiple typed result blocks, including images. Preserve both function name
and call ID when continuing.

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

For legacy `generateContent` with Gemini 3.x, every `FunctionResponse` likewise
requires both `call_id` and function `name` (gemini-3.6).

## Connect remote MCP tools

Interactions can connect directly to a remote MCP server with an `mcp_server`
tool. Only Streamable HTTP is supported, not SSE. Server names cannot contain
hyphens. Optional `headers` and `allowed_tools` provide authentication and
filtering.

```python
tools=[{
    "type": "mcp_server",
    "name": "weather_service",
    "url": "https://example.com/mcp",
    "allowed_tools": ["get_weather"],
}]
```

## Assemble typed SDK argument deltas

In a streamed Interactions call, take each function ID and name from
`step.start` and group state by `event.index`. Typed SDK objects expose
argument fragments when `event.delta.type == "arguments"`; append
`event.delta.partial_arguments` and parse only after
`interaction.completed`.

```python
if event.event_type == "step.delta" and event.delta.type == "arguments":
    current_calls[event.index]["arguments"] += event.delta.partial_arguments
```

At the raw SSE layer, the corresponding discriminant and value are
`arguments_delta` and `arguments`; see
[Interactions API](interactions-api.md#continue-a-streamed-client-side-function-call).

## Avoid structured prose immediately before tool calls

Requiring XML, YAML, or JSON text immediately before a tool call can produce
`Malformed_Function_Call`. Prefer a dedicated working-notes function invoked
alongside the real call. Markdown notes or removing the pre-tool text
requirement are fallback options.

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

## Combine built-in and custom tools

A request can contain built-in tools and custom function tools together.
Computer Use is in public preview on `gemini-3.5-flash`, with browser, mobile,
and desktop environments plus configurable safety and prompt-injection
controls.
