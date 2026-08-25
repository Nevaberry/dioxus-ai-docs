---
name: google-gemini-api-knowledge-patch
description: Google Gemini API
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Google Gemini API Knowledge Patch

Use this skill for Gemini API implementation, migration, model selection,
function calling, structured output, streaming, billing, and lifecycle work.
Start by identifying which API surface the project uses: `generateContent`,
the Interactions API, Live, Batch, or an OpenAI-compatible endpoint. Also
identify the language SDK and whether conversation history is managed by the
SDK or assembled manually.

Prefer concrete model IDs when reproducibility matters. Treat moving aliases,
preview endpoints, quotas, billing state, and lifecycle dates as operational
inputs that should be checked before deployment.

## Reference index

| Reference | Topics |
|---|---|
| [SDK migration](references/sdk-migration.md) | GA package names, clients, async calls, JavaScript streams, automatic tools, parsed output, caches, embeddings |
| [Interactions API](references/interactions-api.md) | `steps`, revision dates, SSE assembly, function continuation, response formats, agents, logs |
| [Thought signatures](references/thought-signatures.md) | Required history replay, sequential and parallel calls, compatibility envelopes, streams, imported traces |
| [Models and lifecycle](references/models-and-lifecycle.md) | Current model IDs, defaults, shutdowns, multimodal endpoints, Live, Batch, research, external files |
| [Function calling and tools](references/function-calling-and-tools.md) | Declarations, tool choice, multimodal results, remote MCP, argument deltas, pre-tool text |
| [Structured outputs](references/structured-outputs.md) | Recursive schemas, streaming JSON, built-in tools, supported schema subset |
| [Billing and limits](references/billing-and-limits.md) | Account tiers and caps, Prepay/Postpay, project caps, quota dimensions, traffic pools |

## Migration priorities

### Use the current SDK packages

Replace the legacy packages with `google-genai`, `@google/genai`, or
`google.golang.org/genai`. Create one client and access models, files, caches,
and other services through it. Generation configuration is per call; Python
async methods live under `client.aio`.

JavaScript responses are flattened: use `response.text`, and iterate the value
returned by `generateContentStream` directly. Python callables passed as tools
execute automatically unless automatic function calling is disabled.

See [SDK migration](references/sdk-migration.md) for language-specific examples
and changes to structured responses, caches, and embeddings.

### Migrate Interactions clients to typed steps

Current Interactions responses use typed `steps`, not flat `outputs`.
`POST /interactions` returns output steps; `GET /interactions/{id}` returns the
full timeline. For stateless continuation, replay the entire preceding steps
array as `input`, then append a `user_input` step.

The SSE lifecycle is:

```text
interaction.created
  → step.start → step.delta → step.stop
  → interaction.completed
  → [DONE]
```

The completion event does not contain assembled steps. Accumulate indexed
deltas, tolerate unknown event variants, and parse function arguments or
structured JSON only when the corresponding output is complete.

Python and JavaScript SDK 2.0.0+ select the new schema. Older clients and REST
revision headers had a dated transition ending June 8, 2026; use the exact
revision rules in [Interactions API](references/interactions-api.md) when
maintaining transition-era code.

### Remove unsupported generation controls

On `gemini-3.6-flash` and `gemini-3.5-flash-lite`, remove `temperature`,
`top_p`, and `top_k`; they are deprecated and ignored, and future generations
will reject them. Replace `thinking_budget` with string-valued
`thinking_level` when moving to 3.6 Flash, and remove `candidate_count` for
Gemini 3.x.

Do not send a prefilled model turn as the last non-empty turn. Use
`system_instruction` or `response_format` to constrain the answer instead.
For legacy `generateContent` with Gemini 3.x, every `FunctionResponse` needs
both `call_id` and function `name`.

## Thought signatures are conversation state

For Gemini 3.x function calling, return each opaque thought signature unchanged
on the exact model part where it arrived. This is mandatory even with minimal
thinking when history is manually assembled. Official SDK history handling is
safe when the complete response object is appended.

Sequential tool loops must retain every signed model-call step since the most
recent user message containing ordinary content. A user message containing
only a function response does not start a new turn.

Parallel calls must stay grouped:

```text
model: [FC1 + signature, FC2]
user:  [FR1, FR2]
```

Only the first parallel function call carries the signature. Do not interleave
calls and results. Also consume streamed responses through `finish_reason`,
because a non-call signature can arrive on an empty-text part. See
[Thought signatures](references/thought-signatures.md) for version differences,
the compatibility envelope, and documented sentinels for imported traces.

## Function calling

Interactions custom functions are direct `{"type": "function", ...}` entries
in `tools`; their `parameters` are object schemas. `tool_choice` supports
`auto`, `any`, `none`, and preview `validated`, with `allowed_tools` for
filtering. Very large or deeply nested schemas can fail in forced-call mode.

For a streamed client-side call, capture its ID and name at `step.start`,
concatenate argument fragments by event index, and parse only after completion.
If the interaction ends in `requires_action`, execute the function and continue
with `previous_interaction_id` plus a matching `call_id`. Server-side tools run
without that round trip and expose paired call/result steps.

Gemini 3-series function results can contain multiple typed blocks, including
images. Preserve the function name and call ID. Remote MCP tools accept only
Streamable HTTP; MCP server names cannot contain hyphens.

Avoid requiring XML, YAML, or JSON prose immediately before a tool call, which
can trigger `Malformed_Function_Call`. Prefer a dedicated notes function or,
secondarily, Markdown notes. See
[Function calling and tools](references/function-calling-and-tools.md).

## Structured output

Put Interactions structured JSON controls in top-level `response_format` as a
text format with `mime_type: application/json` and `schema`. The same field can
be an array for multiple modalities. Image settings also move there, and audio
uses a typed audio format rather than `response_modalities`.

Schemas may recurse with `$ref: "#"`. Supported features include nullable
unions, boolean or schema-valued `additionalProperties`, date/time formats,
numeric bounds, and `prefixItems`, `minItems`, and `maxItems`. Keep schemas
reasonably sized and shallow.

Structured streaming yields partial JSON text. Concatenate all text fragments
in order and validate once complete. On 3-series models, built-in tools and a
structured final response can be combined as a preview feature. See
[Structured outputs](references/structured-outputs.md).

## Model and lifecycle choices

`gemini-3.7-flash` is the GA coding and agentic model. Its introductory pricing
ends December 31, 2026. Other current production choices include
`gemini-3.6-flash` and `gemini-3.5-flash-lite`; both support a one-million-token
context, 64k maximum output, and native Computer Use.

Do not assume a `-latest` alias remains on one generation. Before deploying,
check the concrete successors and cutoff dates for embedding, image, Gemini
2.5, and Flash-Lite workloads in
[Models and lifecycle](references/models-and-lifecycle.md).

The API no longer offers model tuning. Current capabilities instead include
multimodal embeddings, native image and short-video endpoints, stateful Live
sessions, event-driven long-running operations, and Deep Research agents.

## Billing and quota guardrails

Billing plan, usage tier, and account spend cap belong to the Cloud Billing
account and are inherited by linked projects; request quotas are per project,
shared by all its keys. A billing-account cap or zero Prepay balance stops all
linked projects. Project spend caps and balance enforcement can lag by roughly
ten minutes, so they are not hard real-time circuit breakers.

Handle RPM, input TPM, and RPD independently. Paid tiers can also hit a rolling
ten-minute spend-rate limit and receive `429 RESOURCE_EXHAUSTED` while ordinary
quota remains. Failed 400/500 requests consume quota but are not token-billed;
`GetTokens` consumes neither inference quota nor billable tokens.

Priority inference and Batch have distinct limits. Consult
[Billing and limits](references/billing-and-limits.md) before capacity planning
or changing billing accounts.

## Implementation checklist

1. Identify the API surface, SDK package and major version, concrete model ID,
   and whether history is automatic or manual.
2. Check lifecycle status, shutdown dates, aliases, and pricing assumptions.
3. For Interactions, confirm typed steps, response formats, and the correct raw
   SSE or typed-SDK delta representation.
4. Preserve thought signatures, call IDs, function names, ordering, and all
   history required for continuation.
5. Assemble streamed arguments and JSON before parsing; skip and log unknown
   extensible event variants.
6. Treat billing-account state, project quotas, spend rate, traffic class, and
   enforcement lag as separate controls.
