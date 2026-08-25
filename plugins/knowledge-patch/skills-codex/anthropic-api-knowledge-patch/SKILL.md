---
name: anthropic-api-knowledge-patch
description: Anthropic API
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Anthropic API Compatibility and Operations

Use this skill when implementing or reviewing Messages API requests, model
migrations, tool use, streaming, structured output, prompt caching, platform
deployment, rate-limit handling, or Managed Agents integrations.

## Reference index

| Reference | Topics |
| --- | --- |
| [Models and migrations](references/models-and-migrations.md) | Model IDs, Claude 5 migration, thinking, sampling, token budgets, lifecycle, retirement, context, and tool contracts |
| [Tools and streaming](references/tools-and-streaming.md) | Eager tool input, invalid JSON, beta headers, stream aggregation, fallbacks, interrupted streams, hosted tools, and advisor use |
| [Structured output](references/structured-output.md) | JSON schemas, parse helpers, strict tools, complexity ceilings, parsing edge cases, and schema-data safety |
| [Prompt caching](references/prompt-caching.md) | Automatic and explicit breakpoints, TTLs, invalidation, thinking, pre-warming, diagnosis, and isolation |
| [Platforms and limits](references/platforms-and-limits.md) | Hosted API surfaces, identity, inference location, model discovery, rate limits, compliance, workspaces, and Admin APIs |
| [Managed Agents](references/managed-agents.md) | Agents, sessions, events, memory, execution, secrets, schedules, webhooks, budgets, advisors, and repository skills |

## Breaking migration checks

### Replace removed Claude 5 request fields

Fable 5, Mythos 5, Opus 5, and Sonnet 5 reject assistant prefills and
non-default `temperature`, `top_p`, and `top_k`. Use system instructions or a
JSON schema for output shaping, use effort for behavioral control, and move the
top-level `output_format` request field to `output_config.format`.

All Claude 5 targets default to adaptive thinking and reject manual
`budget_tokens`. Keep `max_tokens` large enough for thinking plus visible
output. Request readable reasoning only with `display: "summarized"`.

```python
response = client.messages.create(
    model=model_id,
    max_tokens=65536,
    thinking={"type": "adaptive", "display": "summarized"},
    output_config={"effort": "high", "format": output_format},
    messages=messages,
)
```

Fable 5 and Mythos 5 cannot disable thinking. Sonnet 5 can disable it at any
effort. Opus 5 can disable it only at `high`, `medium`, or `low`; `xhigh` and
`max` return 400. Disabling it on Opus 5 risks visible tool-call text or
internal XML, so do not treat it as a transparent optimization.

### Preserve or remove thinking blocks deliberately

When continuing on the same model, replay `thinking` blocks unchanged. Before
switching models, remove both `thinking` and `redacted_thinking` blocks.
Foreign-model blocks are ignored, but waste request capacity.

### Update old tool contracts

Direct migrations from Claude 3.x to Opus 5 or Sonnet 5 require
`text_editor_20250728` with `str_replace_based_edit_tool` and
`code_execution_20260521`; remove `undo_edit`. Parse tool arguments with a JSON
library and preserve trailing newlines in string arguments.

Haiku 4.5 is different: it rejects adaptive thinking, retains optional manual
extended thinking, accepts only one of `temperature` and `top_p` during a 3.x
migration, and uses `text_editor_20250728` plus
`code_execution_20250825` without `undo_edit`.

### Remove retired beta headers

Effort is generally available and adaptive thinking enables interleaved
thinking. Remove `effort-2025-11-24` and
`interleaved-thinking-2025-05-14`. The older
`token-efficient-tools-2025-02-19` and `output-128k-2025-02-19` headers do
nothing on Claude 4 and later.

## Handle refusals and stops before parsing

Fable 5 and Opus 5 classifier refusals are HTTP 200 responses with
`stop_reason: "refusal"` and a category in `stop_details`. Discard partial
output from a mid-stream Fable refusal. A pre-output Fable refusal is not billed
for input tokens.

Also distinguish `model_context_window_exceeded` from `max_tokens`. For schema
outputs, inspect `stop_reason` before decoding because refusals and truncation
can violate or stop short of the requested schema.

Server-side fallback emits a `fallback` content block with start and stop
events but no deltas. Stream consumers must accept that empty lifecycle.

## Stream tool input safely

Enable unbuffered input per custom tool with `eager_input_streaming: true`.
Omission remains buffered and server-validated; explicit `false` always forces
buffering even if the legacy beta header is present.

```python
tools = [{
    "name": "make_file",
    "eager_input_streaming": True,
    "input_schema": {"type": "object", "properties": {
        "text": {"type": "string"},
    }},
}]
```

A streamed `tool_use` starts with `input: {}`. Concatenate
`input_json_delta.partial_json` by content-block index, parse only after
`content_block_stop`, and never execute malformed or truncated input. Return an
error tool result that preserves the raw input inside a JSON-serialized
`INVALID_JSON` wrapper.

## Use structured output as a parsing contract

The generally available raw request shape is
`output_config.format = {"type": "json_schema", "schema": ...}`. The result
is still a JSON string inside a text content block; select it and decode it.
Python's `messages.parse(..., output_format=Model)` is the exception and
returns the validated object as `response.parsed_output`.

Set `strict: true` independently on each tool that needs grammar-constrained
arguments. Strict and non-strict tools can coexist with a final output schema.
The final-output grammar does not constrain tool calls, tool results, or
thinking.

Budget schema complexity across the whole request: no more than 20 strict
tools, 24 optional parameters, and 16 `anyOf` or type-array parameters.
Compilation can still reject interacting unions and nesting, and times out
after 180 seconds.

## Make prompt caching observable

A request-level `cache_control` consumes one of four breakpoint slots and
targets the last eligible block. A same-TTL explicit control on that block
makes it a no-op; a different TTL or four explicit breakpoints produces 400.
Amazon Bedrock does not support automatic caching.

Keep one-hour breakpoints before five-minute breakpoints. Check
`usage.cache_creation`, `cache_creation_input_tokens`, and
`cache_read_input_tokens` instead of assuming a marked prefix was eligible.
Changing tools, thinking mode, manual budget, or effective effort can
invalidate more of the prefix than changing message content alone.

For a zero-output warm-up, use `max_tokens: 0`, an explicit breakpoint on
shared system text or tools, and a non-whitespace user placeholder. Match the
real request's thinking and effort; do not stream or request structured output.

## Aggregate long streams

Use streaming for large output limits even when only the final message is
needed. Prefer the SDK accumulator: Python `get_final_message()`, TypeScript
`finalMessage()`, Go `message.Accumulate(event)`, Java `MessageAccumulator`,
C# `Aggregate()` or `CollectAsync()`, or Ruby `accumulated_message`. PHP needs
manual accumulation.

With `display: "omitted"`, a thinking block still emits one `signature_delta`
between its start and stop. For interrupted output on 4.6 and later, send the
captured final text block in a new user message and ask the model to continue;
tool-use and thinking fragments cannot be resumed.

## Design for rate limits

Treat RPM, input TPM, and output TPM as independent continuously replenished
buckets. Limits can be enforced over sub-minute windows, and rapid ramps can
trigger acceleration `429` responses. Honor `retry-after` and ramp gradually.

Input-token charging normally counts fresh input plus cache writes, excluding
cache reads; Haiku 3.5 also counts cache reads. Output TPM is charged as tokens
are generated, so `max_tokens` does not reserve the full amount.

Model-family pools can be shared, workspace ceilings may be lower than the
organization's, fast mode has its own pool, and Message Batches and Managed
Agents have separate pools. Use the `anthropic-ratelimit-*` and
`anthropic-fast-*` headers rather than a hard-coded retry model.

## Keep platform surfaces distinct

Claude Platform on AWS is Anthropic-managed with AWS billing and IAM. Amazon
Bedrock's `/anthropic/v1/messages` uses the first-party request shape on
AWS-managed infrastructure. Their model IDs, caching behavior, limits, and
feature availability are not interchangeable.

Discover `max_input_tokens`, `max_tokens`, and capabilities through
`GET /v1/models` or `GET /v1/models/{model_id}`. Treat an ID as a fixed weights
and configuration snapshot, while allowing serving infrastructure and safety
classifiers to evolve.

## Operate Managed Agents defensively

Use `managed-agents-2026-04-01` for the core beta surface. Put `effort` and
`inference_geo` inside the agent's `model` object. Supply an agent `version` on
updates when optimistic concurrency is required; a mismatch returns 409.

Session creation accepts up to 50 initial user-message or outcome events and
can start the loop immediately. Session and thread streams can request delta
previews. Tool output above 100,000 characters spills into a sandbox file, so
preserve the returned path.

Memory listing uses `agent-memory-2026-07-22` instead of the core beta header;
sending both returns 400 and old cursors cannot be reused. Hard session spend
budgets pause with `budget_reached` and resume after the budget changes or is
removed.

## Implementation workflow

1. Resolve the exact model ID and platform before composing request fields.
2. Audit removed sampling, prefill, thinking, tool, and beta-header behavior.
3. Size context and output using discovered limits and current token counts.
4. Treat stop reasons, stream block lifecycles, and tool JSON as untrusted
   control flow.
5. Add explicit parsing, retry, cache, and rate-limit telemetry.
6. Test platform-specific feature boundaries and workspace-level safeguards.
7. For Managed Agents, test concurrency, event replay, memory-header cutover,
   budget pauses, and oversized tool output.

Use the topic references for complete constraints, exact request shapes, and
edge conditions before shipping changes.
