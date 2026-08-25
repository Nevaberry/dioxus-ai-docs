# Interactions API

## Complete the dated `steps` migration (interactions-2026-05)

Python and JavaScript SDK 2.0.0 and later select only the new schema beginning
May 7, 2026. SDK 1.x continued returning the legacy schema until its removal on
June 8, 2026; Interactions calls from those versions then break.

REST clients could opt in before the default flip with
`Api-Revision: 2026-05-20` and, after May 26, temporarily opt out with
`Api-Revision: 2026-05-07`. From June 8 onward, the legacy schema is removed
and the header is ignored.

## Consume typed steps instead of flat outputs

Responses use typed `steps`, not `outputs`. Model content is nested in a
`model_output` step; thoughts, function calls, and server-side tool calls and
results are independent steps.

```json
{
  "steps": [{
    "type": "model_output",
    "content": [{"type": "text", "text": "Hello"}]
  }]
}
```

`POST /interactions` returns output steps only. `GET /interactions/{id}`
returns the full timeline, including `user_input`. SDK convenience accessors
include `output_text`, `output_image`, and `output_audio`.

For stateless history, send the entire preceding `steps` array as the next
request's `input`, then append the new turn as a `user_input` step. Function
calls remain top-level `function_call` steps. Server-side tools produce paired
typed steps such as `google_search_call` and `google_search_result`.

## Assemble the revised SSE lifecycle

The revised order is `interaction.created`, one or more `step.start` →
`step.delta` → `step.stop` cycles, `interaction.completed`, then `[DONE]`.
It replaces `interaction.start`, `content.*`, and `interaction.complete`.

The completion event has final status and usage but no `steps`; assemble steps
from indexed events. Unary responses already contain assembled steps. Raw SSE
`step.delta` values are discriminated by `delta.type`: `text`, `image`,
`arguments_delta`, and optional thinking fields. Image data is base64. Function
arguments arrive as partial JSON strings in `arguments_delta.arguments`.
Thinking can include `thought_summary` followed by `thought_signature`.

Event and delta variants are extensible. Log and skip unknown types instead of
failing the stream.

## Continue a streamed client-side function call

A function call's `step.start` contains its ID and name with empty arguments.
Concatenate every matching arguments fragment and parse only when the step is
finished. Typed SDK event objects can expose this as delta type `arguments`
with `partial_arguments`; see
[Function calling and tools](function-calling-and-tools.md#assemble-typed-sdk-argument-deltas).

When completion status is `requires_action`, execute the function and start a
second streamed interaction with the first interaction ID and matching call ID:

```json
{
  "previous_interaction_id": "v1_...",
  "input": [{
    "type": "function_result",
    "name": "get_weather",
    "call_id": "call_123",
    "result": {
      "content": [{"type": "text", "text": "{\"weather\":\"sunny\"}"}]
    }
  }],
  "stream": true
}
```

Server-side tools need no client round trip and expose call/result activity as
typed steps. One request may mix server-side and client-side tools, but only
client-side functions leave the interaction in `requires_action`.

## Use polymorphic `response_format`

Output controls are top-level and type-discriminated. For structured JSON,
remove `response_mime_type` and nest `mime_type` and the schema beneath a text
format:

```python
response_format={
    "type": "text",
    "mime_type": "application/json",
    "schema": {
        "type": "object",
        "properties": {"summary": {"type": "string"}},
    },
}
```

Move image settings out of `generation_config.image_config` into an image
format entry. Replace `response_modalities=["audio"]` with `{"type": "audio"}`.
Pass an array for multiple modalities; their stream deltas may interleave.

```python
response_format=[
    {"type": "text"},
    {
        "type": "image",
        "mime_type": "image/jpeg",
        "aspect_ratio": "1:1",
        "image_size": "1K",
    },
]
```

## Stream background agents

Agent interactions use `agent` and `background=True` rather than `model`.
Adding `stream=True` exposes progress, thought summaries, and output through
the same step events.

```python
client.interactions.create(
    agent="deep-research-preview-04-2026",
    input="Research the topic.",
    background=True,
    stream=True,
    agent_config={"type": "deep-research", "thinking_summaries": "auto"},
)
```

## Account for operational field changes

In v1beta, `total_reasoning_tokens` was renamed to `total_thought_tokens`.
Supported Interactions calls expose developer logs for operational inspection.
