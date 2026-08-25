---
name: openai-api-knowledge-patch
description: OpenAI API
version: null
license: MIT
metadata:
  author: Nevaberry
---


# OpenAI API Knowledge Patch

Use this skill when implementing, reviewing, or migrating OpenAI API integrations that
touch Responses, GPT-5.6, tools, prompt caching, service tiers, Realtime, or platform
retirements.

## How to use this patch

1. Identify the endpoint, model family, and processing tier in the application.
2. Check retirement migrations before preserving an older API, model, or alias.
3. Read the matching reference file before changing request or event schemas.
4. Preserve response items and identifiers exactly when chaining state or tool calls.
5. Make storage, reasoning, image detail, cache mode, and service tier explicit when
   their defaults affect privacy, cost, latency, or compatibility.
6. Inspect returned effective fields such as `strict`, `reasoning.context`, and
   `service_tier` instead of assuming the requested behavior was applied.

## Reference index

| Reference | Topics |
| --- | --- |
| [Models, Reasoning, Media, and Prompt Caching](references/models-and-prompt-caching.md) | GPT-5.6 tiers and limits, reasoning, Pro, multimodal detail, cache breakpoints and retention, restricted-access models |
| [Release Lifecycle and Migrations](references/release-lifecycle.md) | Deprecation semantics, alias pinning, shutdown dates, replacements, fine-tuning wind-down |
| [Responses, State, and Safety](references/responses-and-state.md) | Generation count, response chains, storage, stateless replay, streaming, moderation, reasoning context, safety identifiers |
| [Service Tiers and Realtime](references/service-tiers-and-realtime.md) | Flex, Priority, Ultrafast, usage dimensions, Realtime sessions, translation, credentials, GA events |
| [Tools and Structured Output](references/tools-and-structured-output.md) | Structured parsing, function round trips, deferred loading, allowed tools, streaming calls, custom tools, programmatic and multi-agent calls |

## Breaking migrations first

Before making feature changes, search the integration for retired endpoints, models,
headers, and reusable platform objects.

### Replace retired interfaces

- Remove the `OpenAI-Beta: realtime=v1` interface and adopt the released Realtime
  session, credential, endpoint, and event shapes.
- Move Assistants API persistence to Responses plus Conversations before the
  August 26, 2026 shutdown.
- Remove Videos API dependencies before September 24, 2026; no replacement is
  listed for its `sora-2` and `sora-2-pro` models.
- Move reusable prompt objects into application code before `v1/prompts` shuts down
  on November 30, 2026.
- Replace Evals with Promptfoo and Agent Builder workflows with the Agents SDK or
  ChatGPT Workspace Agents before their November 30 shutdowns.
- Migrate supported image generation to `gpt-image-2`; the remaining older image
  models have shutdowns through December 1, 2026.

### Pin behavior-sensitive models

- Treat `legacy` as no-longer-updated, not as a shutdown announcement.
- Treat a deprecation notice as actionable because it includes a shutdown date.
- Do not use moving `chat-latest`, audio, realtime, transcription, or Sora aliases
  when behavior must remain fixed; select a dated model ID.
- Review the full migration tables before retaining GPT-3.5, GPT-4, GPT-4o, GPT-5,
  o-series, Codex, deep-research, realtime, audio, image, or fine-tuned models.

## Responses essentials

### Generation and chains

- Responses produces one generation per request and has no `n` parameter. Send
  separate requests when multiple candidates are required.
- `previous_response_id` carries prior response context but not top-level
  `instructions`; resend stable instructions on every request.
- Earlier input in a response chain remains billable input.

### Storage and stateless execution

- Responses is stored by default. Chat Completions is also stored by default for
  new accounts.
- Set `store: false` for stateless use. Zero Data Retention disables storage
  automatically.
- For stateless reasoning continuity, replay every returned reasoning item with its
  default `encrypted_content`.

### Streaming and moderation

- HTTP `stream=true` uses server-sent events.
- Persistent WebSocket mode accepts incremental input chained with
  `previous_response_id`.
- Moderation scores requested with generation arrive only after the full output;
  partial deltas do not contain them.

## GPT-5.6 request compatibility

### Choose the family member deliberately

- `gpt-5.6` routes to `gpt-5.6-sol`.
- Use `gpt-5.6-terra` for a balanced lower-cost tier and `gpt-5.6-luna` for
  efficient high-volume work.
- Sol and Terra accept roughly 1.05 million input tokens; Luna accepts 400,000.
  All three allow up to 128,000 output tokens.
- Sol and Terra requests above 272,000 input tokens enter different full-request
  pricing. Fast mode accepts long-context prompts for all three family members.

### Set reasoning explicitly

- Supported efforts are `none`, `low`, `medium`, `high`, `xhigh`, and `max`; the
  default is `medium` in standard and Pro modes.
- Responses uses `reasoning: {"effort": "none"}`. Chat Completions uses
  `reasoning_effort: "none"`.
- Chat Completions function tools require effective reasoning `none`. Set it
  explicitly or move reasoning-plus-tools work to Responses.
- Pro is a Responses-only mode on a normal family model, not a separate slug. Mode
  and effort are independent, and Pro starts at `medium` effort.

```json
{
  "model": "gpt-5.6-sol",
  "reasoning": { "mode": "pro", "effort": "medium" }
}
```

### Control reasoning history

- Use `reasoning.context: "all_turns"` with `previous_response_id` only while goals
  and assumptions remain stable.
- Use `current_turn` when earlier reasoning is stale, or omit the field/use `auto`
  and inspect the returned effective value.
- Manual replay must preserve user inputs, output items, item IDs, call IDs, caller
  metadata, and assistant phase values.

## Tools and structured output

### Function schemas and round trips

- In Responses, omitted `strict` attempts strict mode. An incompatible schema falls
  back to best effort and reports `strict: false`; set `strict: false` explicitly
  when non-strict behavior is intended.
- Preserve every output item. Return each function result as
  `function_call_output` with the originating `call_id`.
- A function result is usually a string but may be an array of image or file
  objects.

### Structured data and refusals

- Put raw structured formats under `text.format`.
- Python parse helpers accept a Pydantic model through `text_format`; JavaScript
  helpers accept a Zod format through `text.format`.
- Inspect message content items: a safety refusal is a distinct `refusal` item and
  does not conform to the requested schema.

### Tool orchestration

- Keep `tool_search_call` and `tool_search_output` items in history when deferred
  functions are discovered.
- Use `tool_choice` with `type: "allowed_tools"` to restrict a stable full tool list
  without destroying prompt-cache reuse.
- Do not combine built-in tools with parallel function calling.
- When handling streamed calls, aggregate argument deltas by `output_index` and
  associate them with the call by `item_id`.
- Hosts using programmatic or multi-agent calling must recognize, preserve, and
  replay every specialized call, output, message, caller, and `call_id` item.

## Prompt caching

### Prefer explicit boundaries for measured prefixes

- Implicit caching places a managed breakpoint near the latest user or tool message;
  a changing suffix can therefore displace a stable prefix.
- Use `prompt_cache_options` with `prompt_cache_breakpoint` for measured stable
  boundaries on GPT-5.6 and later.
- Set `prompt_cache_key` and shard busy traffic with a stable mapping that keeps
  identical prefixes on the same key.
- A cache hit still requires an exact rendered-prefix match and at least 1,024
  tokens in that prefix.

### Respect generation-specific retention

- GPT-5.6 uses `prompt_cache_options.ttl`; `30m` is its only supported value and is
  a minimum lifetime.
- Earlier models retain `prompt_cache_retention`, whose `in_memory` and `24h`
  policies have maximum-retention semantics.
- Cache writes appear as `cache_write_tokens` and cost 1.25 times uncached input.
- Do not send explicit cache fields to pre-GPT-5.6 models; they reject those fields.

## Service tiers and Realtime

### Processing tiers

- Flex uses Batch API token rates but can take longer than the SDK's ten-minute
  default timeout. A capacity miss is an unbilled `429 Resource Unavailable`.
- Retry Flex with exponential backoff, or use `service_tier: "auto"` to fall back to
  the project's default processing mode.
- Inspect returned `service_tier`: Priority can be downgraded to `default` by ramp
  limits and billed at Standard rates.
- Priority supports prompt-cache discounts and image inputs, but not long context,
  fine-tuned models, or embeddings.
- Ultrafast for `gpt-5.6-sol` is limited preview and must not be assumed available.

### Realtime transport

- Use `gpt-realtime-2.1` on `/v1/realtime` for stateful voice agents,
  `gpt-realtime-translate` for continuous translation, and
  `gpt-realtime-whisper` for transcript deltas.
- Translation starts without `response.create` or a committed user turn.
- Realtime uses the `OpenAI-Safety-Identifier` header, not the Responses
  `safety_identifier` parameter.
- Client credentials come from `POST /v1/realtime/client_secrets`; GA WebRTC uses
  `/v1/realtime/calls`.
- Update handlers to the GA output-text, output-audio, and output-audio-transcript
  delta event names documented in the Realtime reference.
