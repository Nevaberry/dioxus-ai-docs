# Service Tiers and Realtime

## Flex timeout and retry behavior

Flex applies to Responses and Chat Completions at Batch API token rates, while
retaining prompt-cache discounts. Official SDK requests default to a ten-minute
timeout and automatically retry `408 Request Timeout` twice. Long Flex work may
need a larger client-wide or per-request timeout.

```python
response = client.with_options(timeout=900.0).responses.create(
    model="<supported-model>",
    input="<long-running task>",
    service_tier="flex",
)
```

A Flex capacity shortage returns `429 Resource Unavailable` and does not charge for
the request. Retry with exponential backoff to preserve Flex pricing. To use the
project's default processing mode instead, retry with `service_tier="auto"` or
omit the field.

## Priority defaults and effective tier

Priority can be selected per request with `service_tier="priority"`. A project can
also make Priority the default for requests that omit the field, although the
project-level transition occurs gradually. Inspect the response's `service_tier`
field to determine which tier actually processed a request.

## Priority ramp and compatibility limits

Standard and Priority traffic share the same per-model rate limit. At traffic of at
least one million TPM, increasing TPM by more than 50 percent within 15 minutes may
trigger the ramp limit. Affected Priority requests are processed with
`service_tier="default"` and billed at Standard rates. Shift sustained traffic
gradually.

Priority retains prompt-cache discounts and supports multimodal image inputs. It
does not support long-context requests, fine-tuned models, or embeddings. It has a
per-token premium and fits steady latency-sensitive traffic better than erratic
batch or evaluation workloads.

## Limited-preview and reporting updates (`2026-08-04-2026-08-13`)

Ultrafast is a limited-preview API service tier for `gpt-5.6-sol`, available only
to selected customers. Do not assume a project has access without separate
enablement.

The Usage API and Costs API support API key as a filtering and grouping dimension,
enabling programmatic per-key usage and cost reporting.

## Choose the Realtime workload and model

Use `gpt-realtime-2.1` on `/v1/realtime` for a voice agent that responds, calls
tools, and maintains conversation state. Realtime 2 voice sessions expose
`reasoning.effort`.

Use `gpt-realtime-translate` on `/v1/realtime/translations` for continuous
translation. Use `gpt-realtime-whisper` for live transcript-delta workflows.

## Continuous translation lifecycle

Translation sessions stream translated audio and transcript deltas without the
normal assistant-turn lifecycle. Do not send `response.create`, and do not wait for
the client to commit a user turn before translation begins.

## Safety identifier transport

Realtime uses the `OpenAI-Safety-Identifier` header rather than the Responses
`safety_identifier` parameter.

Put the header on the server-side client-secret request to bind an ephemeral
session, or on a trusted server's WebSocket or unified WebRTC connection. The value
does not carry over from Responses requests or other sessions.

## GA credentials, endpoint, and event shapes

Browser and mobile clients obtain ephemeral credentials with
`POST /v1/realtime/client_secrets`. GA WebRTC setup uses
`/v1/realtime/calls`.

GA session configuration sets `session.type` and places output-audio settings under
`session.audio.output`. Handle the GA stream event names:

- `response.output_text.delta`
- `response.output_audio.delta`
- `response.output_audio_transcript.delta`
