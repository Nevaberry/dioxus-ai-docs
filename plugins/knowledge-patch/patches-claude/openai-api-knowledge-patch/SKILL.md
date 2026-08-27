---
name: openai-api-knowledge-patch
description: OpenAI API
version: null
license: MIT
metadata:
  author: Nevaberry
---


# OpenAI API Knowledge Patch

Use this skill for OpenAI API implementation, migration, debugging, and
operational planning where endpoint semantics, model behavior, tool calling,
caching, service tiers, or product retirements affect the result.

## How to use this skill

1. Identify the endpoint, model ID, processing tier, and state-management
   strategy in the project before changing code.
2. Read only the reference files needed for the task. For migrations, start
   with endpoint lifecycle and then open the feature-specific reference.
3. Preserve response items and identifiers exactly when continuing a tool,
   reasoning, or multi-agent interaction.
4. Treat moving aliases as unpinned behavior. Use dated model IDs when a
   production integration requires stable behavior.
5. Inspect returned effective fields such as `service_tier`, strictness, or
   reasoning context rather than assuming the requested mode was applied.

## Reference index

| Reference | Read for |
|---|---|
| [Endpoint state and lifecycle](references/endpoint-state-and-lifecycle.md) | Responses storage, chaining, streaming, alias movement, shutdowns, migrations, and usage reporting |
| [Models and reasoning](references/models-and-reasoning.md) | GPT-5.6 IDs, limits, effort, persisted reasoning, Pro, multimodal detail, and access previews |
| [Tools and structured output](references/tools-and-structured-output.md) | Parsed output, refusals, function loops, namespaces, allowed tools, streaming calls, custom tools, programmatic tools, and multi-agent responses |
| [Prompt caching](references/prompt-caching.md) | Explicit and implicit caching, breakpoints, cache keys, TTLs, retention, and compatibility |
| [Service tiers](references/service-tiers.md) | Flex, Priority, Ultrafast, retries, capacity, pricing behavior, and limitations |
| [Realtime API](references/realtime.md) | Realtime models, translation, credentials, safety identifiers, WebRTC, and GA events |

## Breaking changes and retirements

### Prefer Responses for stateful migrations

The Assistants API shuts down on August 26, 2026. Migrate persistent assistant
workloads to Responses plus Conversations. Responses produces one generation
per request, stores responses by default, and does not carry top-level
`instructions` through `previous_response_id`; resend stable instructions.

### Remove obsolete beta and product surfaces

- The Realtime beta header interface was removed on May 12, 2026. Use the GA
  Realtime interface and event shapes.
- The Videos API and its Sora 2 models shut down on September 24, 2026 without
  a listed replacement.
- Reusable prompt objects and `v1/prompts` shut down November 30, 2026. Keep
  prompt content in application code.
- The Evals dashboard and API and Agent Builder shut down November 30, 2026.
  Follow their distinct migration paths.

### Plan model shutdowns by exact ID

Do not infer a migration from a family name alone. The shutdown schedule has
separate dates and replacements for chat snapshots, legacy base models,
fine-tuned models, image models, GPT-5 and o3 snapshots, and audio/realtime
families. Read [Endpoint state and lifecycle](references/endpoint-state-and-lifecycle.md)
before changing model IDs.

### Distinguish deprecation from legacy

Deprecation includes an announced shutdown date. `legacy` means the surface
no longer receives updates and may be deprecated later. Preview models can
receive much less notice than generally available models, so inventory exact
IDs and avoid moving aliases for pinned production behavior.

## Responses API quick reference

### Chaining and billing

`previous_response_id` carries prior response context, but earlier chain input
tokens remain billable and top-level `instructions` must be resent. In manual
replay, preserve response items instead of reconstructing only visible text.

### Storage and stateless reasoning

Responses are stored by default; Chat Completions are also stored by default
for new accounts. Set `store: false` for stateless use. When reasoning must
survive stateless turns, replay every reasoning item with its
`encrypted_content`. Zero Data Retention disables storage automatically.

### Strict functions

Omitting `strict` in a Responses function attempts strict mode. An incompatible
schema falls back to best effort and reports `strict: false`; set the field
explicitly when non-strict behavior is intentional.

### Streaming

HTTP `stream=true` uses server-sent events. Persistent WebSocket mode supports
incremental input chained by `previous_response_id`. Moderation scores requested
with a generation arrive only after the full output, not with partial deltas.

## GPT-5.6 quick reference

### Choose the family member explicitly

- `gpt-5.6` aliases the flagship `gpt-5.6-sol`.
- `gpt-5.6-terra` is the balanced lower-cost tier.
- `gpt-5.6-luna` targets efficient high-volume work.

Sol and Terra accept roughly 1.05M input tokens, while Luna accepts 400K; all
three allow up to 128K output tokens. Sol and Terra inputs above 272K tokens
use different full-request pricing.

### Set reasoning fields for the endpoint

The available effort values are `none`, `low`, `medium`, `high`, `xhigh`, and
`max`, with `medium` as the default. Responses uses
`reasoning: {"effort": "none"}`; Chat Completions uses
`reasoning_effort: "none"`.

Chat Completions function tools require effective effort `none`; its default
`medium` is incompatible. Set `reasoning_effort` explicitly or use Responses
for reasoning with tools.

### Use Pro as a mode

Pro is a Responses-only reasoning mode on a normal family model, not a model
slug. Set `reasoning.mode: "pro"` independently of effort; supported Pro
efforts begin at `medium`.

### Control retained reasoning

Use `reasoning.context: "all_turns"` with `previous_response_id` only while
goals and assumptions remain stable. Use `current_turn` when old reasoning is
stale, or `auto`/omission for the default, and inspect the returned effective
value.

## Tools and structured output quick reference

### Handle parsed data and refusals separately

Responses structured formats live under `text.format`. SDK parse helpers can
accept Pydantic or Zod schemas, but a safety refusal is a distinct `refusal`
content item and is not schema-conforming parsed data.

### Preserve the function-call protocol

Each `function_call` has JSON-encoded `arguments` and a `call_id`. Keep all
response output items, execute the call, and return a `function_call_output`
with the same `call_id`. Tool results may be strings or arrays of image/file
objects.

### Keep tool lists cache-stable

Use an `allowed_tools` choice to restrict a stable full tool list per turn.
Namespaces group functions, while `defer_loading: true` lets `tool_search`
discover them on GPT-5.4 or later. Retain tool-search items in history.

### Know the parallel-call boundaries

Built-in tools cannot be combined with parallel function calling.
`parallel_tool_calls: false` permits at most one call in a turn. Multiple calls
from a fine-tuned model disable strict mode for those calls.

## Prompt caching quick reference

For GPT-5.6 and later, use `prompt_cache_key` for reliable routing and shard
busy shared keys with a stable mapping. Exact prefix matching still applies.
Keep total traffic across prefixes sharing a key near 15 requests per minute.

Use `prompt_cache_options` with `prompt_cache_breakpoint` for a measured stable
boundary. The only TTL is `30m`, which is a minimum lifetime. Explicit mode can
write the latest four breakpoints; implicit mode uses one slot itself and can
write the latest three explicit breakpoints. Lookup examines up to the latest
50 breakpoints and requires at least 1,024 rendered prefix tokens.

Do not send the newer caching fields to pre-GPT-5.6 models. Their
`prompt_cache_retention` field has different maximum-retention semantics.

## Service-tier quick reference

### Flex

Flex uses Batch API token rates on Responses and Chat Completions. SDK clients
default to a ten-minute timeout and retry HTTP 408 twice; lengthen the timeout
for long work. A `429 Resource Unavailable` is not charged. Back off to retain
Flex pricing, or retry with `auto`/omission to use the project default.

### Priority

Priority can be selected per request or set as a gradually applied project
default. Check the response `service_tier`. Standard and Priority share
per-model rate limits, and a rapid traffic ramp at one million TPM or more can
fall back to default processing and Standard billing.

Priority supports prompt-cache discounts and image inputs, but not long
context, fine-tuned models, or embeddings. It is best suited to steady,
latency-sensitive traffic.

### Limited-access processing

Ultrafast is limited preview for selected `gpt-5.6-sol` customers. Do not
assume access. Fast mode accepts inputs over 272K tokens on all three GPT-5.6
family members.

## Realtime quick reference

- Use `gpt-realtime-2.1` on `/v1/realtime` for stateful voice agents;
  Realtime 2 voice sessions expose `reasoning.effort`.
- Use `gpt-realtime-translate` on `/v1/realtime/translations` for continuous
  translation and `gpt-realtime-whisper` for transcript-delta workflows.
- Continuous translation does not use the normal assistant-turn lifecycle:
  do not send `response.create` or wait for a committed user turn.
- Browser and mobile clients obtain ephemeral credentials from
  `POST /v1/realtime/client_secrets`; GA WebRTC uses `/v1/realtime/calls`.
- Realtime sends the safety identifier through the
  `OpenAI-Safety-Identifier` header, not a Responses request parameter.

## Operational checks

- Attach a stable, privacy-preserving `safety_identifier` to ordinary API
  requests; generation-time cyber or biology review may refuse or pause a
  stream for several seconds.
- Set image or PDF detail explicitly when cost or latency matters. `auto` can
  retain original image dimensions or use high-detail PDF page images.
- For cost attribution, the Usage and Costs APIs can filter and group by API
  key.
- For approved defensive-security access, verify separate Daybreak and Red
  provisioning before selecting their model IDs.
