# Realtime API

Source batches: `realtime-api` and `release-lifecycle`.

## Models, endpoints, and session types

Use `gpt-realtime-2.1` on `/v1/realtime` for a voice agent that responds,
calls tools, and maintains conversation state. Realtime 2 voice sessions expose
`reasoning.effort`.

Use dedicated surfaces for other live workflows:

- Continuous translation uses `gpt-realtime-translate` on
  `/v1/realtime/translations`.
- Live transcript-delta workflows use `gpt-realtime-whisper`.

## Continuous translation lifecycle

Translation sessions stream translated audio and transcript deltas without the
normal assistant-turn lifecycle. Do not send `response.create`, and do not wait
for the client to commit a user turn before translation begins.

## Safety identifier transport

Realtime uses the `OpenAI-Safety-Identifier` header instead of the Responses
`safety_identifier` parameter. Put the header on either:

- the server-side client-secret request that binds an ephemeral session, or
- a trusted server's WebSocket or unified WebRTC connection.

The value does not carry over from Responses requests or other sessions.

## GA credentials and WebRTC

Browser and mobile clients obtain ephemeral credentials with:

```text
POST /v1/realtime/client_secrets
```

GA WebRTC setup uses:

```text
/v1/realtime/calls
```

## GA configuration and events

GA session configuration sets `session.type` and nests output-audio settings
under `session.audio.output`.

Update stream handlers to these GA event names:

- `response.output_text.delta`
- `response.output_audio.delta`
- `response.output_audio_transcript.delta`

## Beta removal and future family migration

The `OpenAI-Beta: realtime=v1` interface was removed May 12, 2026. The released
Realtime interface differs from the beta.

On January 20, 2027, migrate families as follows:

- `gpt-realtime` and GPT-4o realtime families to `gpt-realtime-2.1`
- realtime mini variants to `gpt-realtime-2.1-mini`
- GPT audio and GPT-4o audio families to `gpt-audio-1.5`
- `gpt-4o-mini-transcribe-2025-03-20` to
  `gpt-4o-mini-transcribe-2025-12-15`
