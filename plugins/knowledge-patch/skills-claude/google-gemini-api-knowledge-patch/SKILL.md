---
name: google-gemini-api-knowledge-patch
description: Google Gemini API
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Google Gemini API Knowledge Patch

Load this skill when building or reviewing applications that call the Gemini
API, migrate to the Google Gen AI SDK, use Interactions, manage function calls
or structured output, choose current endpoints, or diagnose quota and billing
behavior.

Prefer project manifests, runtime responses, and tests when they disagree with
guidance here. Pin concrete endpoint IDs for reproducible workloads, and check
lifecycle metadata before deploying a long-lived integration.

## Reference Index

| Reference | Topics |
| --- | --- |
| [Function Calling and Thought Signatures](references/function-calling-and-signatures.md) | Signature round trips, call ordering, tool declarations, MCP, multimodal results, streamed arguments |
| [Google Gen AI SDK Migration](references/genai-sdk-migration.md) | Package replacement, centralized clients, async access, response shapes, automatic calls, caches, embeddings |
| [Interactions API](references/interactions-api.md) | `steps`, revisions, stateless history, SSE lifecycle, continuation, response formats, background agents |
| [Limits and Billing](references/limits-and-billing.md) | Billing tiers, Prepay/Postpay, project caps, quotas, spend rate, priority and batch pools |
| [Models, Media, and Lifecycle](references/models-media-and-lifecycle.md) | Endpoint selection, removals, media, embeddings, Live sessions, long-running work, tuning |
| [Structured Outputs](references/structured-outputs.md) | Recursive schemas, stream assembly, built-in tools, supported schema subset |

## Breaking Changes First

### Migrate Interactions consumers to typed steps

Current Interactions responses expose typed `steps`, not a flat `outputs`
array. Treat model output, thoughts, client function calls, and server-side tool
activity as separate step variants. Streaming clients must assemble indexed
steps from `step.start`, `step.delta`, and `step.stop`; the final completion
event does not repeat them.

For continuation, return prior `steps` as input or submit a `function_result`
with the matching interaction and call IDs. See
[Interactions API](references/interactions-api.md).

### Preserve thought signatures with function calls

When manually managing Gemini 3.x history, replay each opaque thought
signature unchanged on the exact function-call part that carried it. A
sequential loop must preserve all signed calls in the current turn. Parallel
calls must remain grouped in one model message, followed by their grouped
function responses.

The SDK handles this when the complete response is appended to history. REST
and compatibility-layer clients must preserve the fields themselves. See
[Function Calling and Thought Signatures](references/function-calling-and-signatures.md).

### Replace legacy SDK packages and shapes

Use the GA Google Gen AI packages and a centralized client. Move generation
options into each call's `config`; in Python use `client.aio` for async calls.
In JavaScript read `response.text` directly and iterate the object returned by
`generateContentStream`. See
[Google Gen AI SDK Migration](references/genai-sdk-migration.md).

### Remove unsupported generation controls

For `gemini-3.6-flash` and `gemini-3.5-flash-lite`, remove `temperature`,
`top_p`, and `top_k`; they are ignored and future generations can reject them.
Replace
`thinking_budget` with string-valued `thinking_level` where supported, and do
not send `candidate_count` to Gemini 3.x.

Do not prefill a final model turn: a request ending in a non-empty `model`
turn is rejected. Put output constraints in `system_instruction` or
`response_format` instead.

### Migrate before endpoint shutdowns

Aliases move, preview endpoints disappear, and stable families have scheduled
successors. Pin concrete IDs, record lifecycle metadata with the deployment,
and schedule migrations before the published cutoff. Use
[Models, Media, and Lifecycle](references/models-media-and-lifecycle.md) for
the current mappings and dates.

## Common Implementation Patterns

### Create an Interactions function

Declare each custom function directly in the `tools` array:

```python
weather_tool = {
    "type": "function",
    "name": "get_weather",
    "description": "Get weather for a city.",
    "parameters": {
        "type": "object",
        "properties": {"city": {"type": "string"}},
        "required": ["city"],
    },
}

interaction = client.interactions.create(
    model="MODEL_ID",
    input="Weather in Paris?",
    tools=[weather_tool],
)
```

Use `tool_choice` for automatic, forced, prohibited, or validated calling.
Return client-executed results with both `name` and `call_id`; results may
contain multiple typed text or image blocks.

### Continue a streamed function call

Capture the function ID and name from `step.start`, concatenate every argument
fragment for the same event index, and parse JSON only when the call is
complete. If the interaction ends in `requires_action`, execute the function
and create a continuation with `previous_interaction_id` plus a matching
`function_result`.

Server-side tools do not require this round trip. A request may combine them
with client functions; only an outstanding client function produces
`requires_action`.

### Request typed final output

Interactions use a top-level, discriminated `response_format`:

```python
response_format={
    "type": "text",
    "mime_type": "application/json",
    "schema": Result.model_json_schema(),
}
```

Multiple modalities use an array of text, image, or audio format entries.
Their deltas may interleave, so route each delta by its type. For structured
JSON streaming, concatenate text fragments in order and validate once the
document is complete.

### Use the centralized generation client

```python
from google import genai

client = genai.Client()
response = client.models.generate_content(
    model="MODEL_ID",
    contents="Summarize the input.",
    config={"max_output_tokens": 200},
)
```

Python callables passed as tools execute automatically unless automatic
function calling is disabled. Pydantic response schemas are validated into
`response.parsed`. Cached content is created through `client.caches` and then
referenced by name in generation configuration.

### Choose a stable endpoint deliberately

For new general coding and agentic workloads, evaluate `gemini-3.7-flash`.
For existing Interactions workloads, account for endpoint-specific thinking
defaults and remove controls the selected endpoint ignores. For deterministic
operations, never depend on `*-latest` aliases.

Image, video, audio, TTS, embedding, and Live workloads have distinct endpoint
families and lifecycle schedules. Confirm the modality and input constraints
in [Models, Media, and Lifecycle](references/models-media-and-lifecycle.md).

## Operational Checks

### Diagnose a 400 response

Check, in order:

1. The last non-empty turn is not a prefilled `model` turn.
2. Every required Gemini 3.x function call retains its thought signature.
3. Parallel calls and responses were not interleaved.
4. A legacy `generateContent` function response includes both `call_id` and
   function `name`.
5. Removed sampling fields and unsupported `candidate_count` are absent.
6. Function and response schemas are not excessively large or deeply nested.
7. Structured or XML pre-tool prose is not provoking a malformed call.

### Diagnose a 429 response

Rate dimensions, a rolling spend-rate ceiling, account funds, and project
spend caps are independent. A project can have RPM and TPM available yet hit
the paid-tier spend-rate limit. Keys in one project share quota, while the
billing plan and account cap apply across linked projects.

Failed 400 and 500 requests still consume quota even when their tokens are not
billed. Consult [Limits and Billing](references/limits-and-billing.md) before
changing retry behavior or distributing keys.

### Review streaming code

- Consume through the terminal event or `finish_reason`; a signature can
  arrive on an empty-text part.
- Dispatch extensible events and deltas by type, logging and skipping unknown
  variants rather than failing the stream.
- Keep per-index state for interleaved steps and modalities.
- Assemble partial function arguments and structured JSON before parsing.
- Expect the completion event to carry status and usage, not the assembled
  output steps.

### Review long-lived deployments

- Pin endpoint IDs and track their lifecycle stage and shutdown date.
- Plan around introductory pricing end dates and account-wide spend caps.
- Prefer event-driven completion for batch jobs and long-running operations.
- Preserve Live session resumption handles and handle `GoAway` before
  disconnect.
- Do not design around model tuning; the API no longer offers a tunable model.
