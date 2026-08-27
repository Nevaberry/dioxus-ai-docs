# Tools, Betas, and Streaming

## Eager tool-input streaming

Batch `fine-grained-tool-streaming` adds per-tool eager input. All targets
support unbuffered tool-input streaming when the request streams and an
individual user-defined tool sets `eager_input_streaming: true`. Omitting the
field retains buffered, server-validated parameter streaming.

The legacy `fine-grained-tool-streaming-2025-05-14` beta header now supplies
eager behavior only for tools where the field is unset. Explicit `false` always
forces buffering.

```python
tools=[{
    "name": "make_file",
    "eager_input_streaming": True,
    "input_schema": {"type": "object", "properties": {"text": {"type": "string"}}},
}]
```

## Accumulating tool input

A streamed `tool_use` block opens with `input: {}`. Accumulate each
`input_json_delta.partial_json` string by content-block index and parse only at
`content_block_stop`. Eager fragments are not server-validated and a
`max_tokens` stop can truncate them. Guard parsing and never execute malformed
input.

Return failure as an error tool result whose string content preserves the raw
input in an `INVALID_JSON` wrapper. Serialize the wrapper with a JSON library,
not interpolation or concatenation.

```json
{
  "type": "tool_result",
  "tool_use_id": "toolu_...",
  "is_error": true,
  "content": "{\"INVALID_JSON\":\"<unparseable input>\"}"
}
```

## Multiple beta features

Batch `streaming-and-betas` defines multi-beta syntax. Raw HTTP uses one
comma-separated `anthropic-beta` header, while SDK beta calls use a `betas`
list. The `ant` CLI also needs a single comma-separated `--beta` value; when the
flag is repeated, only its first occurrence currently takes effect.

```text
anthropic-beta: feature1,feature2
--beta feature1,feature2
```

## Aggregating complete messages

For large output ceilings, stream to keep the connection alive even when
incremental output is not needed. SDK accumulators yield the same complete
`Message` as a non-streaming call:

- Python: `get_final_message()`.
- TypeScript: `finalMessage()`.
- Go: `message.Accumulate(event)`.
- Java: `MessageAccumulator`.
- C#: `Aggregate()` or `CollectAsync()`.
- Ruby: `accumulated_message`.
- PHP: manually accumulate events.

## Unusual block lifecycles

Each server-side fallback boundary emits a `fallback` content block as adjacent
`content_block_start` and `content_block_stop` events with no deltas. Consumers
must accept this empty lifecycle.

With thinking set to `display: "omitted"`, no `thinking_delta` arrives, but a
thinking block still opens, receives one `signature_delta`, and closes:

```text
content_block_start(thinking) -> signature_delta -> content_block_stop
```

## Recovering an interrupted stream

Claude 4.5 and earlier can resume by prefilling a new assistant message with
captured partial output. Claude 4.6 and later reject that approach: append a new
user message that contains the partial text and explicitly asks to continue.

```python
messages.append({
    "role": "user",
    "content": f"Your previous response ended with {partial_text}. Continue from there.",
})
```

Only the latest text block is resumable. Partially streamed tool-use and
thinking blocks cannot be recovered.

## MCP tunnel migration

Tunnel management moved from the Admin API's `/v1/organizations/tunnels` to
`/v1/tunnels` on the Claude API. The new route needs
`mcp-tunnels-2026-06-22` and WIF scope `workspace:manage_tunnels`. The old route
exists only for a migration window.

## Advisor tool

The beta advisor tool pairs a faster executor with a higher-intelligence
advisor during generation. Enable `advisor-tool-2026-03-01`. Limit each advisor
response with `tools[].max_tokens` when full-length advice is unnecessary.

This direct tool is separate from Managed Agents advisor roster entries, which
are documented in [Managed Agents](managed-agents.md).

## Hosted-tool response pruning

`web_search_20260318` and `web_fetch_20260318` accept `response_inclusion` so an
agentic loop can omit consumed result blocks from subsequent API responses.
