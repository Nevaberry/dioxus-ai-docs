# Models, Reasoning, Media, and Prompt Caching

## GPT-5.6 family selection and limits (`gpt-5.6`)

The `gpt-5.6` alias routes to flagship `gpt-5.6-sol`. Choose
`gpt-5.6-terra` for the balanced lower-cost tier and `gpt-5.6-luna` for
efficient high-volume work.

Sol and Terra have roughly 1.05 million input tokens of context; Luna has
400,000. All three allow 128,000 output tokens. Sol and Terra requests above
272,000 input tokens enter different full-request pricing.

## Reasoning effort and endpoint fields

The family supports `none`, `low`, `medium`, `high`, `xhigh`, and `max`. Omission
defaults to `medium` in both standard and Pro modes. Preserve the old effective
effort during migration, then tune it deliberately.

Responses:

```json
{"reasoning":{"effort":"none"}}
```

Chat Completions:

```json
{"reasoning_effort":"none"}
```

Chat Completions function tools require effective reasoning `none`; its default
`medium` is incompatible. Set `reasoning_effort` explicitly or move a workflow
that combines reasoning and tools to Responses.

## Pro mode

Pro is a Responses-only reasoning mode on a normal family model, not a separate
model slug. Mode and effort are independent; supported Pro efforts begin at
`medium`.

```json
{
  "model": "gpt-5.6-sol",
  "reasoning": {"mode": "pro", "effort": "medium"}
}
```

## Multimodal detail defaults

An omitted or `auto` image detail can retain original dimensions. In Responses,
omitted or `input_file.detail: "auto"` may use high-detail PDF page images. Both
behaviors can increase tokens and latency. Chat Completions file inputs do not
offer the same detail control, so set detail explicitly where the endpoint permits
when cost or latency matters.

## Implicit and explicit caching

Implicit caching places a managed breakpoint near the latest user or tool message
and no longer uses 128-token rounding. A changing suffix can therefore displace a
stable prefix. For measured boundaries, use `prompt_cache_options` with one or more
`prompt_cache_breakpoint` markers.

`prompt_cache_options.ttl` replaces deprecated `prompt_cache_retention` on the
newer family. Cache writes appear as `cache_write_tokens` and cost 1.25 times
uncached input.

```json
{
  "prompt_cache_options": {"mode": "explicit", "ttl": "30m"}
}
```

## Cache-key routing and sharding

On GPT-5.6 and later families, set `prompt_cache_key` to use the more reliable
matching path for implicit and explicit caching. The key routes matching work; it
does not relax the requirement for an exact prefix match at a breakpoint.

Keep aggregate traffic across all prefixes sharing one key near 15 requests per
minute. For busier workloads, use a stable shard mapping that keeps identical
prefixes on the same key.

```json
{"prompt_cache_key":"tenant:acme:knowledge-base-v1"}
```

## Breakpoint write and lookup windows

A request can create no more than four new cache writes:

- Implicit mode spends one slot on the managed breakpoint and can write the latest
  three explicit breakpoints.
- Explicit mode can write the latest four explicit breakpoints.
- Breakpoints inherited from earlier turns are read-only.

Lookup considers up to the latest 50 breakpoints and chooses the longest matching
prefix. A rendered prefix must contain at least 1,024 tokens to qualify.

## Breakpoint-compatible blocks

`prompt_cache_breakpoint` ends the prefix after the annotated block. Its only valid
mode is `explicit`.

- Responses supports `input_text`, `input_image`, and `input_file` blocks.
- Chat Completions supports `text`, `image_url`, `input_audio`, `file`, and
  `refusal` blocks.

Request-wide explicit mode without markers disables cache lookup and writes.
Unsupported or non-cacheable blocks return `400 invalid_request_error`. Models
before GPT-5.6 reject `prompt_cache_breakpoint` and `prompt_cache_options`; retain
automatic caching for those models.

## Retention semantics by model generation

For GPT-5.6 and later, `prompt_cache_options.ttl` is a minimum lifetime rather than
a maximum-retention policy. `30m` is the only supported value and the default; a
prefix may remain reusable longer.

Earlier models use `prompt_cache_retention`:

- `in_memory` normally survives 5–10 minutes of inactivity, with a one-hour
  maximum.
- `24h` has a 24-hour maximum.

The `24h` policy is supported by `gpt-5.5`, `gpt-5.5-pro`, `gpt-5.4`, `gpt-5.2`,
`gpt-5.1-codex-max`, `gpt-5.1`, `gpt-5.1-codex`,
`gpt-5.1-codex-mini`, `gpt-5.1-chat-latest`, `gpt-5`, `gpt-5-codex`, and
`gpt-4.1`. The GPT-5.5 pair accepts only `24h`. On older models that accept both,
omission defaults to `24h` without Zero Data Retention and to `in_memory` with it.

## Restricted-access and fast processing updates (`2026-08-04-2026-08-13`)

Responses supports `daybreak-blue-latest`, `daybreak-red-latest`, and
`gpt-5.6-cyber` for approved defensive-security users. Daybreak access requires
separate approval and provisioning. Red access is separately approved for
purpose-trained models such as `gpt-5.6-cyber`.

Fast mode accepts prompts above 272,000 tokens for `gpt-5.6-sol`,
`gpt-5.6-terra`, and `gpt-5.6-luna`; long-context requests no longer need to avoid
that processing mode.
