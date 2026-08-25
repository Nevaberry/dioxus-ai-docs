# Prompt Caching and Rate Limits

## Automatic caching and breakpoints

Batch `prompt-caching` defines request-level automatic caching. The request
control consumes one of four breakpoint slots. If the final target block has an
explicit control with the same TTL, automatic caching is a no-op. A different
TTL or four existing explicit breakpoints produces HTTP 400.

An ineligible final block makes the service walk backward to the nearest
eligible block; if none exists, caching is silently skipped. Amazon Bedrock
does not support automatic caching.

## Cacheable-prefix floors

Minimum cacheable prefixes are:

- 2,048 tokens: Mythos Preview, Opus 4.7, and Haiku 3.5.
- 4,096 tokens: Opus 4.6, Opus 4.5, and Haiku 4.5.
- 1,024 tokens: Opus 4.8, Sonnet 5, Sonnet 4.6, Sonnet 4.5, Opus 4.1, and
  Opus 4.
- 512 tokens: Opus 5, Fable 5, and Mythos 5.

A shorter marked prefix silently runs uncached;
`usage.cache_creation_input_tokens` and `usage.cache_read_input_tokens` both
remain zero.

## TTL ordering and accounting

One-hour and five-minute entries can mix only when all longer-TTL breakpoints
precede the shorter ones. Under `usage.cache_creation`,
`ephemeral_5m_input_tokens + ephemeral_1h_input_tokens` equals
`cache_creation_input_tokens`.

```json
{"cache_control": {"type": "ephemeral", "ttl": "1h"}}
```

## Thinking-aware validity

Thinking blocks cannot have `cache_control`, but replayed thinking in an
earlier assistant turn is cached with later content and counts as input on a
read. A tool-result-only user turn preserves that cache.

Ordinary user content preserves prior thinking on Opus 4.5+ and Sonnet 4.6+.
Earlier Opus and Sonnet targets and every Haiku target strip earlier thinking
and invalidate later message cache entries.

Changing thinking mode, manual `budget_tokens`, or effort always invalidates
message caches and can invalidate tool and system caches depending on target.
Explicitly choosing the target's default effort is equivalent to omitting it
and does not invalidate cache.

## Prefix invalidators

- Changing tools invalidates tool, system, and message caches.
- Toggling web search or citations, or changing speed, preserves only the tool
  cache.
- Changing `tool_choice` or adding/removing images preserves tool and system
  caches but invalidates messages.
- Unstable JSON key ordering in replayed `tool_use` blocks can defeat a hit
  because matching is byte-sensitive.

## Zero-output pre-warming

Use `max_tokens: 0`, an explicit breakpoint on shared system text or tools, and
a non-whitespace placeholder user message. Automatic caching would target the
placeholder, so do not use it for this flow. Keep thinking and effort identical
to real traffic.

```json
{
  "model": "claude-opus-5",
  "max_tokens": 0,
  "system": [{
    "type": "text",
    "text": "Shared instructions",
    "cache_control": {"type": "ephemeral"}
  }],
  "messages": [{"role": "user", "content": "warmup"}]
}
```

Success returns empty content, `stop_reason: "max_tokens"`, populated usage,
and zero output tokens. Zero-output requests reject streaming, enabled manual
thinking, `output_config.format`, forced or `any` tool choice, and Message
Batches.

## Availability and isolation

A newly written entry is unavailable until the first response begins, so
parallel followers must wait. Cache scope is per workspace on the Claude API,
Claude Platform on AWS, and Microsoft Foundry, but per organization on Bedrock
and Google Cloud. Automatic and explicit caching remain eligible for zero data
retention; cache representations and hashes live only in memory, not at rest.

## Continuous and acceleration throttles

Batch `rate-limits` documents independent token buckets for requests per
minute, input tokens per minute, and output tokens per minute. Enforcement may
use sub-minute intervals. Sudden growth can trigger an acceleration-limit 429
even below an apparent steady-state ceiling. Ramp gradually and honor
`retry-after`.

## Spend tiers and AWS billing

Start, Build, and Scale cap calendar-month API spend at $500, $1,000, and
$200,000. Reaching the cap pauses the API until the next month unless it is
raised. Custom-tier organizations have no standard cap, and any organization
may configure a lower self-imposed cap.

Claude Platform on AWS organizations begin on Start and do not automatically
advance. Billing uses AWS Marketplace, spend limits appear under Billing rather
than Limits, and higher limits require an account representative or support;
the normal increase-request flow is unavailable.

## Token accounting

For most targets, ITPM equals `input_tokens + cache_creation_input_tokens`;
cache reads are excluded. `input_tokens` covers content after the final cache
breakpoint, so total input is cache read plus cache creation plus ordinary
input. Haiku 3.5 is the exception that charges cache reads against ITPM.

ITPM is estimated at request start and reconciled to actual input during
processing. OTPM is charged in real time for tokens actually generated;
`max_tokens` does not reserve capacity.

## Shared and dedicated pools

Opus 4.5 through 4.8 share one Opus 4.x pool, and Sonnet 4.5 and 4.6 share one
Sonnet 4.x pool. Opus 5 and Sonnet 5 have separate pools. US and global
`inference_geo` draw from the same capacity.

Supported `speed: "fast"` traffic uses a dedicated pool. Its throttle returns
429 with `retry-after`; `anthropic-fast-*` headers report the pool state.

## Batches, agents, and workspaces

Message Batches have a model-independent pool of 1,000 API requests per minute,
up to 200,000 constituent requests awaiting successful processing, and up to
100,000 items in one batch. Each constituent item consumes queue capacity.

Managed Agents use a separate organization pool: create operations permit 300
requests per minute; retrieve, list, stream, and other reads permit 1,200.

A non-default workspace can set lower RPM, ITPM, OTPM, and spend ceilings.
Unset controls inherit organization limits, unused workspace capacity remains
available elsewhere, the default workspace cannot be capped, and the
organization ceiling wins even if workspace limits sum above it.

## Response headers

`retry-after` is the number of seconds until a retry can succeed. The API also
returns `anthropic-ratelimit-{requests|tokens|input-tokens|output-tokens}-`
`{limit|remaining|reset}` families. Reset values are RFC 3339 timestamps for
full bucket replenishment; remaining token counts are rounded to the nearest
thousand.
