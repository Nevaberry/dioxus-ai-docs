# Tools, Streaming, and Beta Features

This reference consolidates tool and event guidance from
`fine-grained-tool-streaming`, `streaming-and-betas`, and `release-lifecycle`.

## Eager tool-input streaming

### Enable it per tool

Every model supports unbuffered custom-tool input. Use a streaming request and
set `eager_input_streaming: true` on each tool that should receive it. Omission
retains buffered, server-validated parameter streaming.

The per-tool field replaces the legacy
`fine-grained-tool-streaming-2025-05-14` beta header. The header enables eager
streaming only for tools whose field is unset; an explicit `false` still forces
buffering.

```python
tools=[{
    "name": "make_file",
    "eager_input_streaming": True,
    "input_schema": {
        "type": "object",
        "properties": {"text": {"type": "string"}},
    },
}]
```

### Accumulate and validate input

A streamed `tool_use` block initially has `input: {}`. Concatenate every
`input_json_delta.partial_json` string by content-block index and parse only at
`content_block_stop`. Eager fragments have not been server-validated, and a
`max_tokens` stop can truncate them. Catch parsing failures and never execute
invalid input.

Return a failure as an error tool result whose string content preserves the raw
input in an `INVALID_JSON` object. Serialize it with a JSON library rather than
concatenating strings.

```json
{
  "type": "tool_result",
  "tool_use_id": "toolu_...",
  "is_error": true,
  "content": "{\"INVALID_JSON\":\"<unparseable input>\"}"
}
```

## Beta header composition

Raw HTTP combines beta names in one comma-separated `anthropic-beta` header.
SDK beta calls accept a `betas` list. The `ant` CLI needs one comma-separated
`--beta` value; when repeated, only its first value currently takes effect.

```text
anthropic-beta: feature1,feature2
--beta feature1,feature2
```

## Stream aggregation

For large `max_tokens`, stream to keep the connection alive even if only the
complete message is needed. SDK accumulators produce the same `Message` shape
as a non-streaming call:

| SDK | Final-message operation |
| --- | --- |
| Python | `get_final_message()` |
| TypeScript | `finalMessage()` |
| Go | `message.Accumulate(event)` |
| Java | `MessageAccumulator` |
| C# | `Aggregate()` or `CollectAsync()` |
| Ruby | `accumulated_message` |
| PHP | Manual event accumulation |

```python
with client.messages.stream(
    model=model_id,
    max_tokens=128000,
    messages=messages,
) as stream:
    message = stream.get_final_message()
```

## Unusual event lifecycles

### Fallback blocks have no deltas

At each server-side model fallback boundary, the stream emits a `fallback`
content block as a `content_block_start` and `content_block_stop` pair with no
intervening delta. Accept this empty lifecycle rather than treating it as a
protocol error.

### Omitted thinking retains a signature

With thinking configured as `display: "omitted"`, no `thinking_delta` events
arrive. A thinking block still opens, receives one `signature_delta`, and
closes.

```text
content_block_start(thinking) -> signature_delta -> content_block_stop
```

## Recover interrupted streams

Claude 4.5 and earlier can continue from a new assistant prefill containing
captured output. Claude 4.6 and later reject that approach: send a new user
message containing the partial output and an instruction to continue.

Only the most recent text block is resumable. Partially streamed tool-use and
thinking blocks cannot be recovered.

```python
messages.append({
    "role": "user",
    "content": (
        "Your previous response was interrupted and ended with "
        f"{partial_text}. Continue from where you left off."
    ),
})
```

## Advisor tool

The beta advisor tool pairs a faster executor with a higher-intelligence
advisor during generation. Enable `advisor-tool-2026-03-01`. Set
`tools[].max_tokens` to cap an advisor response when full-length guidance is not
needed.

```text
Anthropic-Beta: advisor-tool-2026-03-01
```

This request-level advisor tool is separate from Managed Agents advisor roster
entries described in [Managed Agents](managed-agents.md).

## Prune consumed hosted-tool results

`web_search_20260318` and `web_fetch_20260318` support
`response_inclusion`. Use it to omit already-consumed result blocks from the
API response in long agentic loops.
