# Models, Migrations, and Lifecycle

This reference consolidates model compatibility guidance from
`claude-4.6-model-ids`, `claude-5-migration`, and `release-lifecycle`.

## Model identifiers and snapshot boundaries

### Canonical IDs from the 4.6 generation

Canonical IDs use `claude-{name}-{major}[-{minor}]`; whole-major releases omit
the minor segment. From 4.6 onward, these dateless IDs are pinned snapshots,
not evergreen aliases. Each updated release receives a new ID and its own
deprecation and retirement schedule.

```text
claude-sonnet-4-6
claude-sonnet-5
```

Amazon Bedrock uses `anthropic.claude-{name}-{major}[-{minor}]`. Opus 4.6 is
the final exception with a `-v1` suffix. Sonnet 4.6 and later omit it. Google
Cloud uses the Claude API's dateless ID for 4.6 and later.

```text
anthropic.claude-opus-4-6-v1
anthropic.claude-sonnet-4-6
claude-sonnet-4-6
```

An ID fixes weights and configuration, but not routing, safety classifiers,
sampling logic, or other serving infrastructure. Small observable changes do
not by themselves prove that a snapshot changed.

## Claude 5 request migration

### Thinking controls

All Claude 5 targets default to adaptive thinking and reject manual extended
thinking with `budget_tokens`. Fable 5 and Mythos 5 cannot disable thinking.
Sonnet 5 permits `thinking: {"type": "disabled"}` at every effort. Opus 5
permits it only at `high`, `medium`, or `low`; `xhigh` and `max` return 400.
Disabling thinking on Opus 5 can expose tool calls as text or leak internal XML
into visible output.

Readable thinking is absent unless `display: "summarized"` is requested.
`max_tokens` is the hard combined ceiling for thinking and visible output.

```python
thinking={"type": "adaptive", "display": "summarized"},
output_config={"effort": "high"},
```

### Prefills, sampling, and output format

Fable 5, Mythos 5, Opus 5, and Sonnet 5 reject assistant-message prefills.
They also return 400 for non-default `temperature`, `top_p`, or `top_k`. Replace
formatting prefills with system instructions or structured output, steer with
effort, and migrate the deprecated top-level `output_format` request parameter
to `output_config.format`.

```python
output_config={"format": output_format}
```

SDK request types may still expose sampling fields. Opus 4.7 and later and
Mythos Preview likewise reject non-default sampling values, so omit them.

### Thinking-block continuity

Replay `thinking` blocks unchanged when continuing on the model that produced
them. Before replaying history on a different model, strip both `thinking` and
`redacted_thinking`. Foreign-model blocks are silently ignored, but consume
payload capacity unnecessarily.

### Fable and Mythos access

`claude-fable-5` is generally available, supports Priority Tier, and runs
safety classifiers. `claude-mythos-5` is limited to approved Project Glasswing
customers, lacks Priority Tier, and omits those classifiers. Both require
30-day retention and are unavailable with zero-data retention. An ineligible
Fable request on the Claude API returns 400 `invalid_request_error`; retention
can instead be configured per workspace.

### Refusals and server-side fallback

Fable 5 and Opus 5 classifier refusals return HTTP 200 with
`stop_reason: "refusal"` and `stop_details.category`. Fable categories include
`cyber`, `bio`, and `reasoning_extraction`. A pre-output Fable refusal is not
billed for input tokens; discard all partial output from a mid-stream refusal.

Fable 5 accepts the beta `fallbacks` parameter. Opus 5 can request a
classifier-dependent recommended target with `fallbacks: "default"` and the
server-side fallback header. This is unavailable in Message Batches and hosted
platform APIs.

```text
Anthropic-Beta: server-side-fallback-2026-07-01
{"fallbacks":"default"}
```

### Token budgets and tokenizer changes

Sonnet 5's tokenizer uses about 30% more tokens than Sonnet 4.6 while keeping a
default 1M context window and 128k maximum output. Opus 5 uses the Opus 4.7
tokenizer, which may consume roughly 1–1.35 times the tokens of pre-4.7 models,
and provides 1M context without a beta header or long-context premium. Fable 5
and Mythos 5 share the Mythos Preview tokenizer and permit up to 128k output.
Rerun token counting and retune `max_tokens` and compaction thresholds.

Opus 5 beta task budgets expose a running allowance across thinking, tool
calls, tool results, and final output. The minimum is 20k tokens. This allowance
is advisory; per-request `max_tokens` remains hard.

```python
betas=["task-budgets-2026-03-13"],
output_config={
    "effort": "high",
    "task_budget": {"type": "tokens", "total": 128000},
}
```

### Mid-conversation instructions and tools

Opus 5 accepts a `role: "system"` message immediately after a user turn.
Initial instructions still belong in the top-level `system` field, and Sonnet 5
does not support mid-conversation system messages. The
`mid-conversation-tool-changes-2026-07-01` beta lets Opus 5 add or remove tools
between turns without invalidating earlier cache hits.

```text
messages=[
  {"role":"user","content":"Apply the new policy."},
  {"role":"system","content":"Use the revised instructions."}
]
Anthropic-Beta: mid-conversation-tool-changes-2026-07-01
```

Fable 5, Mythos 5, and Opus 4.8 also accept a system message after a user turn
without a beta header. Opus 5, Fable 5, and Mythos 5 have a 512-token minimum
cacheable prompt.

### Opus 5-specific behavior

Research-preview fast mode uses `speed: "fast"` with
`fast-mode-2026-02-01`. Opus 5 does not support web fetch or Priority Tier.
Start `xhigh` and `max` workloads with at least 64k `max_tokens` so thinking and
tool work have room.

```text
Anthropic-Beta: fast-mode-2026-02-01
{"speed":"fast"}
```

### High-resolution images

Opus 4.7 and later automatically accept images up to 2,576 pixels on the long
edge or 3.75 megapixels. A full-resolution image may use about 4,784 tokens,
roughly three times the prior cap. Pointing and bounding-box coordinates map 1:1
to image pixels; remove older scale conversion and downsample when fidelity is
not needed.

### Tool contracts for older-model jumps

Direct moves from Claude 3.x to Opus 5 or Sonnet 5 must use
`text_editor_20250728` with `str_replace_based_edit_tool` and
`code_execution_20260521`, and remove `undo_edit`. Use a standard JSON parser
because escaping may differ. Preserve trailing newlines retained in string
arguments by Claude 4.5 and later.

### Context exhaustion

Claude 4.5 and later return `stop_reason: "model_context_window_exceeded"` for
context exhaustion. Handle it separately from the requested `max_tokens`
ceiling.

### Retired beta headers

Effort is generally available and adaptive thinking enables interleaved
thinking. Remove `effort-2025-11-24` and
`interleaved-thinking-2025-05-14`. The
`token-efficient-tools-2025-02-19` and `output-128k-2025-02-19` headers have no
effect on Claude 4 and later.

### Haiku 4.5 boundary

Haiku 4.5 supports optional manual extended thinking and rejects adaptive
thinking. When migrating from Haiku 3.x, send only one of `temperature` and
`top_p`, use `text_editor_20250728` and `code_execution_20250825`, and remove
`undo_edit`. Haiku 4.5 rate limits are separate from Haiku 3.5.

### Prompt and agent-scaffold retuning

Opus 5 visible responses tend to run longer even at lower effort. State desired
deliverable length explicitly. Remove inherited self-check instructions that
cause over-verification, narrow task scope, and state when delegation is useful
or cap subagent counts because Opus 5 delegates more readily.

## Lifecycle and limit changes

### Lifecycle states and usage audits

Legacy models receive no updates but have no retirement date. Deprecated models
work until their assigned retirement; retired-model requests fail. Publicly
released models receive at least 60 days' retirement notice. Use the Console
usage export, broken down by API key and model, to identify remaining callers.

### Retirement schedule

`claude-mythos-preview` is deprecated in favor of `claude-mythos-5` on covered
Anthropic-operated platforms. Move `claude-opus-4-1-20250805` to
`claude-opus-4-8` before August 5, 2026. Listed Claude 4.0, 3.x, 2.x, 1.x, and
Instant IDs are already retired.

The earliest tentative dates are:

| Snapshot | Earliest retirement |
| --- | --- |
| Opus 4.5 | November 24, 2026 |
| Sonnet 4.5 | September 29, 2026 |
| Haiku 4.5 | October 15, 2026 |
| Opus 4.6 / 4.7 / 4.8 / 5 | February 5 / April 16 / May 28 / July 24, 2027 |
| Sonnet 4.6 / 5 | February 17 / June 30, 2027 |
| Fable 5 | June 9, 2027 |

### Workbench and prompt-tool shutdown

Legacy Workbench access ends August 17, 2026. Saved prompts, variables, and
evals do not migrate automatically, so export them first. The experimental
`/v1/experimental/generate_prompt`, `/v1/experimental/improve_prompt`, and
`/v1/experimental/templatize_prompt` endpoints retire the same day and then
return errors.

### Fast-mode retirement behavior

On Opus 4.7, `speed: "fast"` returns an error. On Opus 4.6 it silently uses
standard speed and pricing. Inspect `usage.speed`; move fast workloads to a
supported newer target.

### One-million-token context

The `context-1m-2025-08-07` header has no effect on Sonnet 4 or 4.5, and
requests above their standard 200k context now fail. Opus 4.6 and Sonnet 4.6
provide 1M context at standard pricing without a beta header and use ordinary
account limits at every length. A 1M request may contain up to 600 images or PDF
pages.

### Discover model limits

`GET /v1/models` and `GET /v1/models/{model_id}` return `max_input_tokens`,
`max_tokens`, and `capabilities`. Discover these values instead of hard-coding
them. Opus 4.6 and Sonnet 4.6 can raise the single-turn output cap to 300k with:

```text
Anthropic-Beta: output-300k-2026-03-24
```
