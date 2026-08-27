# Interactions API

## Migrate on the dated schema schedule

Python and JavaScript SDK 2.0.0 and later select only the new schema beginning
May 7, 2026. SDK 1.x continues to return the legacy schema until its removal on
June 8, when Interactions calls from those versions break.

REST clients can opt in with `Api-Revision: 2026-05-20` before the May 26
default flip. They can temporarily opt out with
`Api-Revision: 2026-05-07` until June 8; after removal, the legacy schema is
gone and the revision header is ignored.

## Consume typed steps

Responses use typed `steps` instead of `outputs`. Model content lives in a
`model_output` step; thoughts, client function calls, server-side tool calls,
and server-side results have their own step types.

```json
{
  "steps": [{
    "type": "model_output",
    "content": [{"type": "text", "text": "Hello"}]
  }]
}
```

`POST /interactions` returns output steps only. `GET /interactions/{id}`
returns the complete timeline, including `user_input`. SDK convenience access
includes `output_text`, `output_image`, and `output_audio`.

For stateless history, send the complete preceding `steps` array as the next
request's `input` and append the new turn as a `user_input` step. Function
calls remain top-level `function_call` steps. Server-executed tools emit paired
typed steps such as `google_search_call` and `google_search_result`.

## Assemble the step-based SSE lifecycle

The revised stream is:

```text
interaction.created
step.start -> step.delta ... -> step.stop
interaction.completed
[DONE]
```

This replaces `interaction.start`, `content.*`, and `interaction.complete`.
The completion event carries final status and usage but no `steps`, so stream
consumers assemble steps by event index. Unary responses return the assembled
steps directly.

`step.delta` is discriminated by `delta.type`. Text and base64 image data use
text and image variants; function arguments arrive as partial argument JSON;
thinking can include `thought_summary` and a final `thought_signature`.
Variants are extensible: log and skip unknown event or delta types rather than
failing the whole stream.

At the wire-schema level, argument fragments are described as an
`arguments_delta` carrying `arguments`. SDKs may normalize that to an
`arguments` delta and `partial_arguments`; handle the representation exposed
by the selected client without parsing until the step finishes.

## Continue a client function call

`step.start` provides the function call's ID and name with empty arguments.
Concatenate all matching argument fragments. When the interaction completes
with `requires_action`, execute the function and start a second streamed
interaction with the first interaction ID and matching call ID:

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

Server-side tools execute without this client round trip and expose their
call/result activity as typed steps. A request can mix server tools and client
functions; only an unfulfilled client call leaves it in `requires_action`.

## Use polymorphic response formats

Output controls live in top-level `response_format`, discriminated by `type`.
For structured JSON, remove `response_mime_type` and put `mime_type` plus the
schema under a text format:

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

Move image settings out of `generation_config.image_config` and into an image
format entry. Replace `response_modalities=["audio"]` with
`{"type": "audio"}`. Request several modalities with an array; their deltas
can interleave in the same stream.

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

Agent interactions use `agent` with `background=True` rather than `model`.
Add `stream=True` to receive progress, thought summaries, and output through
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

The updated managed agent `antigravity-preview-05-2026` uses 3.6 Flash by
default and runs in the remote environment:

```python
client.interactions.create(
    agent="antigravity-preview-05-2026",
    input="Complete the browser task.",
    environment="remote",
)
```

## Account for operational field changes

In v1beta, `total_reasoning_tokens` was renamed to `total_thought_tokens`.
Supported Interactions calls also expose developer logs for operational
inspection.

Batch attribution: `interactions-2026-05`, `gemini-3.6`, and
`release-lifecycle`.
