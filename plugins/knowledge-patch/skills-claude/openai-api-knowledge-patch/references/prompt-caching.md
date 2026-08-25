# Prompt Caching

Source batches: `prompt-caching` and `gpt-5.6`.

## Explicit and implicit caching

Implicit caching places a managed breakpoint near the latest user or tool
message and no longer rounds at 128-token boundaries. A changing suffix can
therefore displace a stable prefix.

For measured stable boundaries, use `prompt_cache_options` with
`prompt_cache_breakpoint`. `prompt_cache_options.ttl` replaces deprecated
`prompt_cache_retention` for GPT-5.6 and later. Cache writes appear as
`cache_write_tokens` and cost 1.25 times uncached input.

```json
{
  "prompt_cache_options": {
    "mode": "explicit",
    "ttl": "30m"
  }
}
```

## Cache-key routing and sharding

On GPT-5.6 and later families, set `prompt_cache_key` to use the more reliable
matching path for implicit and explicit caching. A shared key hits only when
the exact prefix at a breakpoint matches.

Keep aggregate traffic across all prefixes sharing one key near 15 requests
per minute. For busier workloads, shard with a stable mapping that keeps
identical prefixes on the same key.

```json
{"prompt_cache_key":"tenant:acme:knowledge-base-v1"}
```

## Breakpoint write and read windows

A request can create at most four new cache writes:

- Implicit mode spends one slot on its managed breakpoint and can write the
  latest three explicit breakpoints.
- Explicit mode can write the latest four explicit breakpoints.
- Breakpoints inherited from earlier turns remain read-only.

Lookup considers up to the latest 50 breakpoints, selects the longest matching
prefix, and requires the rendered prefix to contain at least 1,024 tokens.

## Breakpoint-compatible blocks

`prompt_cache_breakpoint` ends the prefix after its annotated block and has
only one valid mode: `explicit`.

Supported Responses blocks:

- `input_text`
- `input_image`
- `input_file`

Supported Chat Completions blocks:

- `text`
- `image_url`
- `input_audio`
- `file`
- `refusal`

Request-wide explicit mode with no markers disables caching and cache writes.
Unsupported or non-cacheable blocks return `400 invalid_request_error`.
Models before GPT-5.6 reject both `prompt_cache_breakpoint` and
`prompt_cache_options`; leave their automatic caching behavior in place.

## Retention semantics

### GPT-5.6 and later

`prompt_cache_options.ttl` is a minimum lifetime, not a maximum-retention
policy. `30m` is the only supported value and the default. A cached prefix may
remain reusable longer.

### Earlier models

Earlier models use the maximum-policy field `prompt_cache_retention`:

- `in_memory` normally survives 5–10 minutes of inactivity, with a one-hour
  maximum.
- `24h` has a 24-hour maximum.

The `24h` policy is supported by:

- `gpt-5.5` and `gpt-5.5-pro`
- `gpt-5.4`
- `gpt-5.2`
- `gpt-5.1-codex-max`, `gpt-5.1`, `gpt-5.1-codex`,
  `gpt-5.1-codex-mini`, and `gpt-5.1-chat-latest`
- `gpt-5`, `gpt-5-codex`, and `gpt-4.1`

The GPT-5.5 pair accepts only `24h`. On older models that accept both policies,
omission defaults to `24h` without Zero Data Retention and to `in_memory` with
Zero Data Retention.
