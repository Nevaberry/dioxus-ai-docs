# Models and Migrations

## Pinned dateless identifiers

Batch `claude-4.6-model-ids` defines the 4.6-and-later ID contract. Canonical
IDs use `claude-{name}-{major}[-{minor}]`; whole-major releases omit the minor
segment. These dateless IDs are fixed snapshots, unlike the short dateless
aliases used for earlier releases. Updates receive new IDs and separate
deprecation and retirement schedules.

Amazon Bedrock uses `anthropic.claude-{name}-{major}[-{minor}]`. Opus 4.6 is
the final `-v1` exception (`anthropic.claude-opus-4-6-v1`); Sonnet 4.6 and
later omit the suffix. Google Cloud uses the same dateless ID as the Claude API
for 4.6 and later.

Snapshot stability covers weights and configuration. Routing, serving
infrastructure, safety classifiers, and sampling logic can still change, so a
minor behavior change does not prove that a pinned snapshot changed.

## Claude 5 thinking controls

Batch `claude-5-migration` changes the thinking contract:

- All Claude 5 targets default to adaptive thinking and reject manual extended
  thinking with `budget_tokens`.
- Fable 5 and Mythos 5 cannot disable thinking.
- Opus 5 accepts `thinking: {"type": "disabled"}` only at `high`, `medium`,
  or `low` effort; `xhigh` and `max` return HTTP 400.
- Sonnet 5 accepts disabled thinking at every effort.
- Readable thinking is absent unless `display: "summarized"` is requested.
- `max_tokens` is the hard combined ceiling for thinking and visible output.
- Disabling thinking on Opus 5 can render tool calls as text or expose internal
  XML in visible output.

Pass prior `thinking` blocks back unchanged when continuing with the target
that produced them. Before switching targets, remove both `thinking` and
`redacted_thinking`; foreign thinking is ignored but wastes payload.

## Prefill, output format, and sampling

Fable 5, Mythos 5, Opus 5, and Sonnet 5 reject assistant-message prefills.
Replace formatting prefills with system instructions or structured output.
They also reject non-default `temperature`, `top_p`, and `top_k` with HTTP 400.

Move the deprecated top-level `output_format` into
`output_config={"format": output_format}`. The Python parse helper's separate
convenience contract is documented in [Structured Outputs](structured-outputs.md).

The broader lifecycle boundary applies the same sampling restriction to Opus
4.7 and later and to Mythos Preview, even though SDK request types still expose
the parameters. Steer those targets with effort.

## Access, retention, and classifiers

Fable 5 is generally available, supports Priority Tier, and runs safety
classifiers. Mythos 5 is restricted to approved Project Glasswing customers,
does not support Priority Tier, and omits those classifiers. Both require
30-day retention and are unavailable with zero data retention. Retention may
instead be set per workspace. An ineligible Fable request to the Claude API
returns HTTP 400 `invalid_request_error`.

Fable 5 and Opus 5 classifier refusals use HTTP 200 with
`stop_reason: "refusal"` and `stop_details.category`. Fable categories include
`cyber`, `bio`, and `reasoning_extraction`. A Fable pre-output refusal is not
billed for input tokens. Discard all partial output after a mid-stream refusal.

Fable 5 accepts beta `fallbacks`. Opus 5 accepts `fallbacks: "default"` with
`server-side-fallback-2026-07-01`, selecting a recommended
classifier-dependent target. Server-side fallback is unavailable for Message
Batches and hosted-platform APIs.

## Tokenization, context, and output ceilings

Re-run token counting when changing targets:

- Sonnet 5 uses about 30% more tokens than Sonnet 4.6. It retains a default 1M
  context and 128k maximum output.
- Opus 5 uses the tokenizer introduced in Opus 4.7, approximately 1–1.35 times
  pre-4.7 counts. It provides 1M context without a beta header or long-context
  premium.
- Fable 5 and Mythos 5 share the Mythos Preview tokenizer and permit up to 128k
  output.

Retune `max_tokens`, compaction, and cache thresholds instead of carrying old
counts forward. Opus 5 work at `xhigh` or `max` effort should begin with at
least 64k `max_tokens` so thinking and tool work have room. Visible responses
can remain long even at lower effort, so specify deliverable length explicitly.

Opus 5 beta task budgets track an advisory allowance across thinking, tool
calls, tool results, and final output. The minimum is 20k tokens. Enable with
`task-budgets-2026-03-13` and set
`output_config.task_budget={"type":"tokens","total":128000}`. This does not
replace the hard request-level `max_tokens` ceiling.

Claude 4.5 and later report context exhaustion as
`model_context_window_exceeded`; handle it separately from `max_tokens`.

## Context and image migration boundaries

The `context-1m-2025-08-07` header has no effect on Sonnet 4 or 4.5; requests
beyond their standard 200k context fail. Opus 4.6 and Sonnet 4.6 provide 1M
context at standard pricing without that header, under ordinary account limits,
and allow up to 600 images or PDF pages per 1M-context request.

Opus 4.6 and Sonnet 4.6 can raise the single-turn output cap to 300k with
`output-300k-2026-03-24`.

Opus 4.7 and later accept images automatically up to 2,576 pixels on the long
edge or 3.75 megapixels. Full resolution can cost about 4,784 tokens. Pointing
and bounding-box coordinates now map 1:1 to image pixels; remove old scale
conversion and downsample when full fidelity is unnecessary.

## Tools when migrating from older targets

Direct moves from Claude 3.x to Opus 5 or Sonnet 5 require
`text_editor_20250728` with `str_replace_based_edit_tool` and
`code_execution_20260521`. Remove `undo_edit`. Parse inputs with a standard JSON
parser because escaping can differ, and preserve trailing newlines retained by
Claude 4.5 and later in string arguments.

Haiku 4.5 remains a distinct boundary: it supports optional manual extended
thinking and rejects adaptive thinking. From Haiku 3.x, send only one of
`temperature` and `top_p`, switch to `text_editor_20250728` and
`code_execution_20250825`, remove `undo_edit`, and provision against its
separate rate-limit pool rather than Haiku 3.5 limits.

## Instructions, tools, and target-specific surfaces

Opus 5 accepts a `role: "system"` message immediately after a user turn;
initial instructions stay in the top-level `system`. Sonnet 5 does not support
mid-conversation system messages. Under
`mid-conversation-tool-changes-2026-07-01`, Opus 5 may add or remove tools
between turns without invalidating cache hits for earlier turns. Opus 5, Fable
5, and Mythos 5 lower the minimum cacheable prompt to 512 tokens.

Opus 5 research-preview fast mode requires `speed: "fast"` and
`fast-mode-2026-02-01`. Opus 5 lacks web fetch and Priority Tier.

Remove `effort-2025-11-24` because effort is GA. Adaptive thinking already
enables interleaved thinking, so remove `interleaved-thinking-2025-05-14`.
`token-efficient-tools-2025-02-19` and `output-128k-2025-02-19` have no effect
on Claude 4 and later.

## Prompt and agent-scaffold retuning

Control visible length explicitly. Remove inherited self-check instructions
that cause excessive verification, keep narrow tasks scoped, and state when
delegation is justified or cap subagent counts because Opus 5 delegates more
readily.
