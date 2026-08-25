# Models, endpoints, and lifecycle operations

## Choose current production Flash models (gemini-3.6)

The GA Interactions model IDs are `gemini-3.6-flash` and
`gemini-3.5-flash-lite`. Their default thinking levels are `medium` and
`minimal`, respectively. Both have a one-million-token context window, a
64k-token maximum output, and native Computer Use.

```python
interaction = client.interactions.create(
    model="gemini-3.6-flash",
    input="Describe this image.",
)
```

For both models, `temperature`, `top_p`, and `top_k` are deprecated and ignored;
remove them because future generations will return HTTP 400. When moving to
3.6 Flash, replace `thinking_budget` with `thinking_level` set to `"medium"` or
`"high"`. Remove `candidate_count`, unsupported by Gemini 3.x.

A request whose last non-empty turn has role `model` returns HTTP 400. Do not
prefill a partial answer. Express formatting or preamble-suppression rules with
`system_instruction` or `response_format`.

```python
interaction = client.interactions.create(
    model="gemini-3.6-flash",
    input="Translate 'Hello world' to Spanish.",
    system_instruction="Output only the translation.",
)
```

The managed agent `antigravity-preview-05-2026` uses 3.6 Flash by default and
runs through Interactions in a remote environment.

```python
interaction = client.interactions.create(
    agent="antigravity-preview-05-2026",
    input="Complete the browser task.",
    environment="remote",
)
```

Legacy `generateContent` requires every Gemini 3.x `FunctionResponse` to include
both `call_id` and function `name`.

## Adopt Gemini 3.7 Flash (rolling-2026-08-19)

`gemini-3.7-flash` is generally available and intended for coding and agentic
workflows. Its introductory pricing runs through December 31, 2026; account for
the later price regime when estimating long-lived workloads.

```python
response = client.models.generate_content(
    model="gemini-3.7-flash",
    contents="Implement the requested change.",
)
```

## Pin concrete IDs instead of moving aliases

Some model records expose lifecycle stage and deprecation timeline metadata.
Aliases are mutable: `gemini-pro-latest` and `gemini-flash-latest` moved to
Gemini 3 previews in January 2026; `gemini-3-pro-preview` redirected to
`gemini-3.1-pro-preview` in March; and `gemini-flash-latest` moved again to
`gemini-3.5-flash` in May. Pin a concrete ID for reproducibility.

`gemini-3.5-flash` is GA. `gemini-3.1-pro-preview-customtools` is a distinct
3.1 Pro endpoint tuned to prioritize custom tools such as bash.
`gemini-3.1-flash-lite` is GA but has a May 7, 2027 shutdown date, with
`gemini-3.5-flash-lite` as successor.

## Complete scheduled migrations

- Move Embedding 2 preview to GA `gemini-embedding-2` by August 10, 2026.
- Move Imagen 4 Standard, Ultra, and Fast (`imagen-4.0-*-generate-001`) to
  `gemini-3.1-flash-image` by August 17, 2026.
- Leave `gemini-2.5-flash-image` by October 2, 2026.
- By October 16, 2026, move `gemini-2.5-pro` to
  `gemini-3.1-pro-preview`, `gemini-2.5-flash` to `gemini-3.6-flash`, and
  `gemini-2.5-flash-lite` to `gemini-3.1-flash-lite`.
- Move `gemini-3.1-flash-lite` to `gemini-3.5-flash-lite` by May 7, 2027.
- Move `gemini-embedding-001` to `gemini-embedding-2` by May 14, 2028.

Gemini 2.0 Flash and Flash-Lite stable IDs became unavailable June 1, 2026.
The 3.1 Flash Image and 3 Pro Image previews became unavailable June 25 in
favor of GA IDs. Stable Veo 2.0/3.0 generation IDs became unavailable June 30
in favor of Veo 3.1 preview endpoints or enterprise GA endpoints.

## Select current image and video endpoints

GA native-image IDs are `gemini-3.1-flash-image`, `gemini-3-pro-image`, and the
lower-latency `gemini-3.1-flash-lite-image`. Only
`gemini-3.1-flash-image` accepts video context for image generation.

`gemini-omni-flash-preview` generates 3–10 second, 720p video from text or a
still image and supports conversational edits to that video.

## Use multimodal embeddings and File Search

GA `gemini-embedding-2` embeds text, images, video, audio, and PDFs in one
space. File Search can index and search images with it. Visual-grounding
citations expose `media_id` and `page_numbers`.

## Stream Live and speech models

`gemini-3.1-flash-live-preview` is the current 3.1 audio-to-audio preview, and
`gemini-3.1-flash-tts-preview` is the current TTS preview. TTS output streams
through `streamGenerateContent` or Interactions with `stream: true`.

## Engineer Live session continuity

Live sessions can retain server state for up to 24 hours and return a
`session_resumption` handle. Sliding-window context compression extends long
sessions. A `GoAway` message warns before disconnect.

Automatic VAD can be tuned or disabled in favor of `activityStart` and
`activityEnd`. Separate controls cover interruption, turn coverage, media
resolution, streamed text, and modality-level `usageMetadata`.

## Supply larger external files

Inputs can reference Cloud Storage buckets and public or private presigned
URLs. The per-file limit for these external inputs increased from 20 MB to
100 MB.

## Prefer event-driven long-running operations

Batch jobs and other long-running operations support event-driven completion,
so integrations can replace polling. Batch also supports embedding-model
requests.

## Integrate Deep Research agents

New Deep Research variants support collaborative planning, visualization, MCP
server integration, and File Search. They can stream to a client UI or run a
more comprehensive automated research path.

## Do not plan on model tuning

The final tunable model, Gemini 1.5 Flash 001, shut down in May 2025. No current
model supports tuning.
