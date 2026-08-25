# Prompt Caching

This reference consolidates `prompt-caching` and the cache additions from
`release-lifecycle`.

## Automatic caching and breakpoint conflicts

A single request-level `cache_control` enables automatic caching of the last
cacheable block and advances that point as a conversation grows. It consumes
one of the four breakpoint slots and can coexist with block-level controls.

If the final target block already has an explicit control with the same TTL,
automatic caching is a no-op. A different TTL or four existing explicit
breakpoints returns HTTP 400. If the last block is ineligible, the service walks
backward to the nearest eligible block and silently skips caching when none
exists. Amazon Bedrock does not support automatic caching.

## Diagnose cache misses

Under the cache-diagnosis beta, send the prior message ID as
`diagnostics.previous_message_id`. Inspect the returned `cache_miss_reason` to
find where the new prompt diverged from the previously cached prefix.

```text
Anthropic-Beta: cache-diagnosis-2026-04-07
{"diagnostics":{"previous_message_id":"msg_..."}}
```

## Model-specific cache floors

| Minimum cacheable prefix | Models |
| --- | --- |
| 512 tokens | Opus 5, Fable 5, Mythos 5 |
| 1,024 tokens | Opus 4.8, Sonnet 5, Sonnet 4.6, Sonnet 4.5, Opus 4.1, Opus 4 |
| 2,048 tokens | Mythos Preview, Opus 4.7, Haiku 3.5 |
| 4,096 tokens | Opus 4.6, Opus 4.5, Haiku 4.5 |

A shorter marked prefix runs uncached without an error. Both
`usage.cache_creation_input_tokens` and `usage.cache_read_input_tokens` stay
zero.

## TTL ordering and accounting

One request may mix one-hour and five-minute cache entries only when every
one-hour breakpoint precedes all five-minute breakpoints.

```json
{"cache_control": {"type": "ephemeral", "ttl": "1h"}}
```

Cache-write usage is split under `usage.cache_creation`.
`ephemeral_5m_input_tokens + ephemeral_1h_input_tokens` equals
`cache_creation_input_tokens`.

## Thinking-aware cache validity

Thinking blocks cannot carry `cache_control` themselves. Replayed thinking in
earlier assistant turns is cached with later content and counts as input when
read. Tool-result-only user turns preserve that cache.

Ordinary user content preserves prior thinking on Opus 4.5 and later and
Sonnet 4.6 and later. Earlier Opus and Sonnet models and every Haiku model strip
prior thinking and invalidate subsequent message cache entries.

Changing thinking mode, manual `budget_tokens`, or effective effort always
invalidates message caches and may invalidate tool and system caches depending
on the model. Explicitly setting effort to the model default is equivalent to
omitting it and does not invalidate the cache.

## Prefix invalidators and exact replay

| Request change | Cache effect |
| --- | --- |
| Tool definitions | Invalidates tool, system, and message caches |
| Web search, citations, or speed | Preserves only the tool cache |
| `tool_choice` | Preserves tool and system; invalidates messages |
| Add or remove images | Preserves tool and system; invalidates messages |

Prefix matching is byte-sensitive. Unstable JSON key ordering in replayed
`tool_use` blocks can defeat cache hits even when the parsed values match.
Serialize replayed blocks deterministically.

Opus 5's `mid-conversation-tool-changes-2026-07-01` beta is the exception for
supported between-turn tool changes: it can preserve cache hits on earlier
turns.

## Zero-output pre-warming

Use `max_tokens: 0` with an explicit breakpoint on a shared system prompt or
tool definition and a non-whitespace placeholder user message. Automatic
caching would target the placeholder, so do not use it for this case. Keep
thinking and effort identical to production traffic.

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

A successful warm-up returns `content: []`, `stop_reason: "max_tokens"`, a
populated usage object, and zero output tokens.

Zero-output requests reject:

- `stream: true`.
- `thinking.type: "enabled"`.
- `output_config.format`.
- Forced or `any` tool choice.
- Message Batches.

## Availability, propagation, and isolation

A newly written entry is not available until the first response begins.
Parallel follower requests must wait for that point.

Caches are workspace-isolated on the Claude API, Claude Platform on AWS, and
Microsoft Foundry. They are organization-isolated on Amazon Bedrock and Google
Cloud. Automatic and explicit caching remain eligible for zero-data retention;
cache representations and hashes are held only in memory, not stored at rest.
