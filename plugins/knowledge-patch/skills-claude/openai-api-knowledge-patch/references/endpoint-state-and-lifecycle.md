# Endpoint State and Lifecycle

Source batches: `responses-api`, `release-lifecycle`, and
`2026-08-04-2026-08-13`.

## Responses request semantics

### One generation per request

Responses has no `n` parameter and returns one generation per request. Make
separate requests when an application needs multiple candidate outputs.

### Chained context and billing

`previous_response_id` carries prior response context but does not carry
top-level `instructions`; resend stable instructions on every request. Earlier
input tokens in the chain are still billed as input tokens.

### Storage and stateless reasoning

Responses are stored by default, as are Chat Completions for new accounts. Set
`store: false` for stateless use. To preserve reasoning across stateless turns,
replay every returned reasoning item with its default `encrypted_content`.
Zero Data Retention flows disable storage automatically.

### Function strictness

Responses function definitions are internally tagged. Omitting `strict`
attempts strict mode rather than preserving the former non-strict default. An
incompatible schema falls back to best-effort calling and reports
`strict: false`; set it explicitly to force non-strict behavior.

```json
{
  "type": "function",
  "name": "lookup",
  "parameters": {
    "type": "object",
    "properties": {}
  },
  "strict": false
}
```

### Streaming transport and moderation

HTTP `stream=true` uses server-sent events. Persistent WebSocket mode supports
incremental inputs chained with `previous_response_id`. Moderation scores
requested with a generation arrive only after the full output and are not
included with partial deltas.

## Lifecycle semantics

### Deprecation, legacy, and notice windows

Deprecation begins when announced and includes a shutdown date. `legacy`
means an API or model no longer receives updates and is likely to be deprecated
later. Unless safety or compliance requires faster action, generally available
models receive at least six months' notice, specialized chat, Codex, and
deep-research variants receive three months, and preview models may receive
only about two weeks.

### Moving aliases

`chat-latest` follows the regularly updated Instant model used in ChatGPT; use
it to test that behavior, not as a stable production target. Unversioned audio,
realtime, transcription, and Sora aliases have also moved between dated
snapshots. Use a dated ID when behavior must remain pinned.

## Shutdown and migration schedule

### July replacement wave

The July 23 shutdown covered computer-use and GPT-4o search previews,
`gpt-5-chat-latest`, `gpt-5.1-chat-latest`, GPT-5/5.1/5.2 Codex variants, and
o3/o4 deep-research models. Use `gpt-5.6-terra` for computer/search and
mini-Codex workloads and `gpt-5.6-sol` for the other chat, Codex, and research
IDs.

### Chat snapshots — August 10, 2026

`gpt-5.2-chat-latest` and `gpt-5.3-chat-latest` shut down on August 10, 2026.
Migrate both to `gpt-5.6-sol`.

### Realtime beta interface — removed May 12, 2026

The `OpenAI-Beta: realtime=v1` interface was removed on May 12, 2026. Migrate
beta integrations to the released Realtime API; its interface differs from the
beta.

### Assistants API — August 26, 2026

The Assistants API shuts down on August 26, 2026. Migrate persistent assistant
integrations to the Responses API plus the Conversations API.

### Videos API — September 24, 2026

The Videos API and all listed `sora-2` and `sora-2-pro` aliases and snapshots
shut down on September 24, 2026. No replacement is listed.

### Legacy models — September 28, 2026

`gpt-3.5-turbo-instruct`, `babbage-002`, `davinci-002`, and
`gpt-3.5-turbo-1106` shut down on September 28, 2026. Their listed
replacements are `gpt-5.4-mini` or `gpt-5-mini`.

### Legacy base models — October 23, 2026

The October 23 shutdown includes `gpt-3.5-turbo-0125` aliases; GPT-4 and GPT-4
Turbo aliases and snapshots; `gpt-4o-2024-05-13`; `gpt-4.1-nano`; `o1`;
`o1-pro`; `o3-mini`; and `o4-mini`.

- Use GPT-5.6 Sol for GPT-4, GPT-4o, o1, and o3 workloads.
- Use Sol with `reasoning.mode: "pro"` for `o1-pro`.
- Use Terra for GPT-3.5 and o4-mini workloads.
- Use Luna for GPT-4.1 nano workloads.

### Fine-tuned models — October 23, 2026

The same wave removes these fine-tuned models and maps them to replacement
bases:

| Removed model | Replacement base |
|---|---|
| `ft-gpt-3.5-turbo` | GPT-5.4 mini |
| `ft-gpt-4` | GPT-5.5 |
| `ft-gpt-4.1-nano-2025-04-14` | GPT-5.4 nano |
| `ft-babbage-002` | GPT-5.4 mini |
| `ft-davinci-002` | GPT-5.4 mini |
| `ft-o4-mini-2025-04-16` | GPT-5.6 Terra |

### Reusable prompts — November 30, 2026

Reusable prompt objects and `v1/prompts` shut down on November 30, 2026. Move
prompt content into application code instead of creating or referencing prompt
objects.

### Evals — October 31 and November 30, 2026

Existing Evals become read-only on October 31. The Evals dashboard, API, and
documented graders shut down November 30. The documented migration path uses
Promptfoo; fine-tuning follows its own schedule.

### Agent Builder — November 30, 2026

Agent Builder shuts down on November 30, while ChatKit remains available.
Migrate workflows to the Agents SDK or ChatGPT Workspace Agents.

### Image models — May 12 through December 1, 2026

`dall-e-2` and `dall-e-3` were removed May 12. `gpt-image-1` shuts down
October 23; `gpt-image-1-mini`, `gpt-image-1.5`, and
`chatgpt-image-latest` shut down December 1. Move these image workloads to
`gpt-image-2`.

### GPT-5 and o3 snapshots — December 11, 2026

The following snapshots shut down December 11:

- `gpt-5-2025-08-07` and `o3-2025-04-16` move to `gpt-5.6-sol`.
- `gpt-5-mini-2025-08-07` moves to Terra.
- `gpt-5-nano-2025-08-07` moves to Luna.
- `gpt-5-pro-2025-10-06` and `o3-pro-2025-06-10` move to Sol with
  `reasoning.mode: "pro"`.

### Self-serve fine-tuning — January 6, 2027

New training is already unavailable to organizations without prior
fine-tuning and, since July 2, to organizations without fine-tuned-model
inference in the preceding 60 days. Remaining active customers lose job
creation on January 6, 2027. Inference continues only until each underlying
base model is deprecated.

### Audio and Realtime families — January 20, 2027

On January 20, 2027:

- `gpt-realtime` and GPT-4o realtime families move to `gpt-realtime-2.1`.
- Their mini variants move to `gpt-realtime-2.1-mini`.
- GPT audio and GPT-4o audio families move to `gpt-audio-1.5`.
- `gpt-4o-mini-transcribe-2025-03-20` moves to
  `gpt-4o-mini-transcribe-2025-12-15`.

## Usage reporting

The Usage API and Costs API can filter and group by API key, enabling
programmatic per-key reporting and analysis.
