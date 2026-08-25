---
name: anthropic-api-knowledge-patch
description: Anthropic API
version: null
license: MIT
metadata:
  author: Nevaberry
---

# Anthropic API Compatibility Guidance

Use this skill when building or migrating integrations for the Messages API,
hosted platform variants, Managed Agents, structured outputs, tools, streaming,
prompt caching, model selection, or rate-limit handling. Treat the project's
actual SDK types, API responses, and model metadata as authoritative when they
differ from this rolling guidance.

## Reference index

| Reference | Topics |
| --- | --- |
| [Models and migrations](references/models-and-migrations.md) | Model IDs, thinking, sampling, context, token budgets, migration contracts, refusals, images |
| [Platforms and lifecycle](references/platforms-and-lifecycle.md) | Retirement, model discovery, AWS surfaces, identity, compliance, enterprise administration |
| [Structured outputs](references/structured-outputs.md) | JSON schemas, parse helpers, strict tools, schema limits, parsing safeguards |
| [Tools and streaming](references/tools-and-streaming.md) | Eager input, stream aggregation and recovery, beta headers, hosted tools, MCP tunnels |
| [Caching and rate limits](references/caching-and-rate-limits.md) | Cache breakpoints, TTLs, invalidation, pre-warming, token buckets, spend and workspace limits |
| [Managed Agents](references/managed-agents.md) | Agents, sessions, event streams, memory, secrets, schedules, budgets, advisors, repository skills |

## Migration triage

Before changing a production target:

1. Resolve the exact model ID and query `/v1/models/{model_id}` for advertised
   context, output, and capability limits.
2. Remove assistant prefills and non-default sampling controls for targets that
   reject them.
3. Move final structured output from top-level `output_format` to
   `output_config.format`; keep the Python parse helper's convenience argument
   only when using that helper.
4. Recount tokens and retune `max_tokens`, compaction, and cache breakpoints.
5. Audit tool versions, remove `undo_edit`, and parse every tool input with a
   real JSON parser.
6. Treat `model_context_window_exceeded`, `max_tokens`, and `refusal` as
   separate stop conditions.
7. Remove retired beta headers and confirm whether the destination surface
   supports each remaining beta.

## Claude 5 breaking changes

Claude 5 targets default to adaptive thinking. Manual extended thinking with
`budget_tokens` is rejected. Fable 5 and Mythos 5 cannot disable thinking;
Opus 5 can disable it only at `high`, `medium`, or `low` effort, and Sonnet 5
can disable it at every effort. Request `display: "summarized"` when readable
thinking is needed.

```python
thinking={"type": "adaptive", "display": "summarized"}
output_config={"effort": "high"}
```

`max_tokens` is still the hard ceiling for thinking and visible output.
Disabling thinking on Opus 5 can expose tool calls as text or internal XML, so
do not use it as a routine latency optimization.

Fable 5, Mythos 5, Opus 5, and Sonnet 5 reject assistant-message prefills and
non-default `temperature`, `top_p`, and `top_k`. Use system instructions,
effort, or structured output instead.

Replay thinking blocks unchanged only to the target that produced them. Strip
both `thinking` and `redacted_thinking` before replaying a conversation to a
different target.

## Model identity and lifecycle

From the 4.6 generation onward, dateless IDs such as
`claude-sonnet-4-6` are pinned snapshots, not evergreen aliases. Whole-major
IDs omit the minor component, as in `claude-sonnet-5`. Each ID has its own
deprecation and retirement schedule.

An ID pins weights and configuration, but serving infrastructure, routing,
safety classifiers, and sampling logic may still change. Do not infer a new
snapshot solely from a small behavioral change.

Lifecycle states have different operational meanings:

- Legacy targets receive no updates but have no assigned retirement date.
- Deprecated targets work until their retirement date.
- Retired targets reject requests.
- Public releases receive at least 60 days' retirement notice.

Use Console usage export to find callers by API key and model. Do not hard-code
limits when `/v1/models` exposes `max_input_tokens`, `max_tokens`, and
`capabilities`.

## Structured output quick reference

The GA raw request shape is `output_config.format` with `type: "json_schema"`
and a `schema`. The result is JSON text in a text content block; select that
block and decode it.

```python
response = client.messages.create(
    model=model_id,
    max_tokens=256,
    messages=[{"role": "user", "content": "Extract the order number."}],
    output_config={"format": {
        "type": "json_schema",
        "schema": schema,
    }},
)
data = json.loads(next(b.text for b in response.content if b.type == "text"))
```

The Python `messages.parse` helper is the exception: it accepts
`output_format=SomePydanticModel` and returns `response.parsed_output`.

Set `strict: true` on each tool whose name and arguments must conform to its
`input_schema`. A final-output grammar does not constrain tool calls, tool
results, or thinking.

Always inspect `stop_reason` before parsing. Refusals and truncation can violate
the requested schema. Treat `enum` and `const` comparisons case-insensitively
and avoid values distinguished only by capitalization.

## Streaming safely

Enable eager input per user-defined tool with `eager_input_streaming: true`.
The old fine-grained streaming beta acts only as a fallback for tools where the
field is unset; explicit `false` keeps buffered validation.

A streamed `tool_use` starts with `input: {}`. Concatenate
`input_json_delta.partial_json` by content-block index and parse only after
`content_block_stop`. Eager fragments are unvalidated and can be truncated by
`max_tokens`; never execute invalid input. Return a failed tool result with the
raw input encoded by a JSON library under an `INVALID_JSON` wrapper.

Use streaming for large output ceilings even when only the final message is
needed. Prefer the SDK accumulator: `get_final_message()` in Python,
`finalMessage()` in TypeScript, `Accumulate` in Go, `MessageAccumulator` in
Java, `Aggregate` or `CollectAsync` in C#, and `accumulated_message` in Ruby.
PHP needs manual accumulation.

At a server-side fallback boundary, accept an empty `fallback` content-block
lifecycle. When thinking display is omitted, accept a thinking block containing
only a `signature_delta`.

## Prompt caching essentials

Request-level `cache_control` consumes one of four breakpoint slots. It is a
no-op when the final target already has an explicit control with the same TTL;
a different TTL or four existing explicit controls returns HTTP 400. If the
final block is ineligible, automatic caching searches backward for an eligible
block.

Place all one-hour breakpoints before five-minute breakpoints. The TTL-specific
counts under `usage.cache_creation` add up to
`cache_creation_input_tokens`.

Cache matching is prefix-sensitive. Tool definitions, thinking settings,
effort, tool choice, images, citations, web search, speed, and unstable JSON
serialization can invalidate different cache layers. Consult the caching
reference before changing any of them.

For deterministic pre-warming, use `max_tokens: 0`, an explicit breakpoint on
shared tools or system content, and a non-whitespace user placeholder. Keep
thinking and effort identical to production traffic.

## Rate-limit handling

The Messages API independently enforces RPM, input-token, and output-token
token buckets, possibly over sub-minute intervals. Ramp traffic gradually;
honor `retry-after` after both ordinary and acceleration-limit 429 responses.

For most targets, ITPM equals `input_tokens + cache_creation_input_tokens` and
excludes cache reads; Haiku 3.5 also charges cache reads. OTPM is charged as
tokens are generated, not reserved from the requested output ceiling.

Rate-limit pools can be shared across related 4.x targets, separate for newer
targets, or dedicated to supported fast mode. Workspace safeguards can lower
limits without partitioning unused capacity, and the organization-wide ceiling
still applies.

## Managed Agents safety checks

Use optimistic concurrency by sending an agent `version` on updates; a mismatch
returns 409. Omitting it performs an unconditional update.

Treat session budgets as hard controls: reaching one pauses the session with
`stop_reason: "budget_reached"`; changing or removing it resumes work.
Deployment budgets apply independently to every launched session.

Memory list calls under `agent-memory-2026-07-22` must replace the older beta
header, not accompany it. Old cursors are incompatible, `depth` is 0, 1, or
omitted, and `path_prefix` must end in `/` and match complete path segments.

Tool output beyond 100,000 characters spills into a sandbox file. Follow the
returned path rather than assuming the truncated preview is complete.

Keep secrets in vaults and inject them at egress. For federated API access,
prefer SDK-managed exchange and refresh of short-lived credentials over static
keys.

## Verification checklist

- Query the exact target's capabilities instead of inferring them by family.
- Verify hosted-platform ID syntax and feature availability independently.
- Exercise streaming consumers against empty fallback and signature-only blocks.
- Parse structured output only after checking the terminal stop reason.
- Log workspace ID and every rate-limit header needed for incident diagnosis.
- Test cache-hit behavior after any tool, thinking, media, or serialization change.
- Audit all beta headers during upgrades; some must be removed, not accumulated.
- Export legacy Workbench data before shutdown deadlines.
