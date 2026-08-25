# Release Lifecycle and Migrations

## Interpret lifecycle states correctly

Deprecation begins when announced and includes a shutdown date. `legacy` only
means that an API or model no longer receives updates and is likely to be
deprecated later.

Unless safety or compliance requires faster action, the normal notice windows are
at least six months for generally available models, three months for specialized
chat, Codex, and deep-research variants, and potentially about two weeks for
preview models.

## Pin moving aliases when behavior matters

`chat-latest` follows the regularly updated Instant model used in ChatGPT and is
suited to testing that behavior, not pinning production behavior. Unversioned
audio, realtime, transcription, and Sora aliases have also moved between dated
snapshots. Use a dated ID when behavior must remain fixed.

## Migrate retired APIs and platform features

| Feature | Shutdown or state | Required action |
| --- | --- | --- |
| Realtime beta header | Removed May 12, 2026 | Replace `OpenAI-Beta: realtime=v1` with the released Realtime API; its interface differs from beta. |
| Assistants API | August 26, 2026 | Move persistent assistants to Responses plus Conversations. |
| Videos API and listed `sora-2` / `sora-2-pro` aliases and snapshots | September 24, 2026 | Remove the dependency; no replacement is listed. |
| Reusable prompt objects and `v1/prompts` | November 30, 2026 | Move prompt content into application code. |
| Evals | Read-only October 31; dashboard, API, and documented graders shut down November 30, 2026 | Migrate documented evaluation workflows to Promptfoo; fine-tuning has a separate schedule. |
| Agent Builder | November 30, 2026 | Move workflows to the Agents SDK or ChatGPT Workspace Agents; ChatKit remains available. |

## Migrate chat, search, research, and Codex models

The July 23, 2026 replacement wave shut down computer-use and GPT-4o search
previews, `gpt-5-chat-latest`, `gpt-5.1-chat-latest`, GPT-5/5.1/5.2 Codex
variants, and o3/o4 deep-research models.

- Use `gpt-5.6-terra` for computer/search and mini-Codex workloads.
- Use `gpt-5.6-sol` for the other chat, Codex, and research IDs.

`gpt-5.2-chat-latest` and `gpt-5.3-chat-latest` shut down August 10, 2026. Move
both to `gpt-5.6-sol`.

## Migrate legacy base models

| Shutdown | Retired models | Replacement |
| --- | --- | --- |
| September 28, 2026 | `gpt-3.5-turbo-instruct`, `babbage-002`, `davinci-002`, `gpt-3.5-turbo-1106` | `gpt-5.4-mini` or `gpt-5-mini` |
| October 23, 2026 | `gpt-3.5-turbo-0125` aliases | `gpt-5.6-terra` |
| October 23, 2026 | GPT-4 and GPT-4 Turbo aliases and snapshots, `gpt-4o-2024-05-13`, `o1`, `o3-mini` | `gpt-5.6-sol` |
| October 23, 2026 | `o1-pro` | `gpt-5.6-sol` with `reasoning.mode: "pro"` |
| October 23, 2026 | `o4-mini` | `gpt-5.6-terra` |
| October 23, 2026 | `gpt-4.1-nano` | `gpt-5.6-luna` |

## Migrate fine-tuned model bases

The following fine-tuned models shut down October 23, 2026:

| Retired model | Replacement base |
| --- | --- |
| `ft-gpt-3.5-turbo` | GPT-5.4 mini |
| `ft-gpt-4` | GPT-5.5 |
| `ft-gpt-4.1-nano-2025-04-14` | GPT-5.4 nano |
| `ft-babbage-002` | GPT-5.4 mini |
| `ft-davinci-002` | GPT-5.4 mini |
| `ft-o4-mini-2025-04-16` | GPT-5.6 Terra |

## Consolidate image generation

`dall-e-2` and `dall-e-3` were removed May 12, 2026. `gpt-image-1` shuts down
October 23. `gpt-image-1-mini`, `gpt-image-1.5`, and `chatgpt-image-latest` shut
down December 1. Move these image workloads to `gpt-image-2`.

## Migrate GPT-5 and o3 snapshots

On December 11, 2026, these snapshots shut down:

- Move `gpt-5-2025-08-07` and `o3-2025-04-16` to `gpt-5.6-sol`.
- Move `gpt-5-mini-2025-08-07` to `gpt-5.6-terra`.
- Move `gpt-5-nano-2025-08-07` to `gpt-5.6-luna`.
- Move `gpt-5-pro-2025-10-06` and `o3-pro-2025-06-10` to `gpt-5.6-sol` with
  `reasoning.mode: "pro"`.

## Plan for the self-serve fine-tuning wind-down

New training is already unavailable to organizations without prior fine-tuning
and, since July 2, to organizations without fine-tuned-model inference in the
preceding 60 days. Remaining active customers lose job creation on January 6,
2027. Inference continues only until each underlying base model is deprecated.

## Migrate realtime, audio, and transcription models

On January 20, 2027:

- Move `gpt-realtime` and GPT-4o realtime families to `gpt-realtime-2.1`.
- Move their mini variants to `gpt-realtime-2.1-mini`.
- Move GPT audio and GPT-4o audio families to `gpt-audio-1.5`.
- Move `gpt-4o-mini-transcribe-2025-03-20` to
  `gpt-4o-mini-transcribe-2025-12-15`.
