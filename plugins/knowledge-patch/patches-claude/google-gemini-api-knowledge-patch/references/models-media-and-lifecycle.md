# Models, Media, and Lifecycle

## Pin IDs instead of moving aliases

Some endpoint records publish lifecycle stage and deprecation timelines.
Aliases are mutable: `gemini-pro-latest` and `gemini-flash-latest` moved to
Gemini 3 previews in January 2026; `gemini-3-pro-preview` redirected to
`gemini-3.1-pro-preview` in March; and `gemini-flash-latest` moved again to
`gemini-3.5-flash` in May. Pin a concrete ID when reproducibility matters.

## Select current general-purpose endpoints

`gemini-3.7-flash` is GA and intended for coding and agentic workflows. Its
introductory pricing ends December 31, 2026, which matters for longer-lived
cost estimates.

```python
response = client.models.generate_content(
    model="gemini-3.7-flash",
    contents="Implement the requested change.",
)
```

The GA Interactions IDs `gemini-3.6-flash` and `gemini-3.5-flash-lite` default
to `medium` and `minimal` thinking, respectively. Both have a one-million-token
context window, a 64k-token maximum output, and native Computer Use.

For these endpoints, `temperature`, `top_p`, and `top_k` are deprecated and
ignored; remove them before future generations begin rejecting them with HTTP
400. When moving to 3.6 Flash, replace `thinking_budget` with string-valued
`thinking_level` (`medium` or `high`). Gemini 3.x does not support
`candidate_count`.

Requests whose last non-empty turn has role `model` return HTTP 400. Do not
append a partial answer to steer completion; put formatting or preamble rules
in `system_instruction` or `response_format`.

`gemini-3.5-flash` is GA. `gemini-3.1-pro-preview-customtools` is a separate
3.1 Pro endpoint tuned to prioritize custom tools such as bash.
`gemini-3.1-flash-lite` is GA but has a May 7, 2027 shutdown in favor of
`gemini-3.5-flash-lite`.

## Schedule forced migrations

- Move Embedding 2 preview to GA `gemini-embedding-2` by August 10, 2026.
- Move Imagen 4 Standard, Ultra, and Fast (`imagen-4.0-*-generate-001`) to
  `gemini-3.1-flash-image` by August 17, 2026.
- Leave `gemini-2.5-flash-image` by October 2, 2026.
- By October 16, 2026, replace `gemini-2.5-pro`, `gemini-2.5-flash`, and
  `gemini-2.5-flash-lite` with `gemini-3.1-pro-preview`, `gemini-3.6-flash`,
  and `gemini-3.1-flash-lite`, respectively.
- Replace `gemini-3.1-flash-lite` with `gemini-3.5-flash-lite` by May 7, 2027.
- Replace `gemini-embedding-001` with `gemini-embedding-2` by May 14, 2028.

Gemini 2.0 Flash and Flash-Lite stable IDs became unavailable June 1, 2026.
The 3.1 Flash Image and 3 Pro Image previews became unavailable June 25 in
favor of GA IDs. Stable Veo 2.0 and 3.0 generation IDs became unavailable June
30 in favor of Veo 3.1 preview endpoints or enterprise GA endpoints.

## Choose current image and video endpoints

GA native-image IDs are `gemini-3.1-flash-image`, `gemini-3-pro-image`, and
the lower-latency `gemini-3.1-flash-lite-image`. Only
`gemini-3.1-flash-image` accepts video context for image generation.

`gemini-omni-flash-preview` generates 3–10 second 720p video from text or a
still image and supports conversational edits to generated video.

## Use multimodal embeddings and File Search

GA `gemini-embedding-2` embeds text, images, video, audio, and PDFs in one
space. File Search can use it to index and search images. Visual-grounding
citations expose `media_id` and `page_numbers`.

## Stream Live audio and speech

`gemini-3.1-flash-live-preview` is the current 3.1 audio-to-audio preview, and
`gemini-3.1-flash-tts-preview` is the current TTS preview. TTS output streams
through `streamGenerateContent` or Interactions with `stream: true`.

Live sessions can retain server-side state for up to 24 hours and return a
`session_resumption` handle. Sliding-window context compression extends long
sessions, and `GoAway` warns before disconnection.

Automatic VAD can be tuned or disabled in favor of `activityStart` and
`activityEnd`. Separate controls govern interruption, turn coverage, media
resolution, streamed text, and modality-level `usageMetadata`.

## Combine built-in and custom tools

A request can combine built-in tools with custom function tools. Computer Use
is also in public preview on `gemini-3.5-flash`, with browser, mobile, and
desktop environments plus configurable safety and prompt-injection controls.

## Supply larger external files

The API accepts Cloud Storage buckets and public or private presigned URLs as
input sources. The per-file limit for these external inputs is 100 MB, raised
from 20 MB.

## Prefer events for long-running work

Batch jobs and other long-running operations support event-driven completion,
allowing integrations to replace polling. Batch processing also accepts
embedding-endpoint requests.

## Use current Deep Research integrations

New Deep Research agent variants add collaborative planning, visualization,
MCP server integration, and File Search. They can stream results to a client UI
or run a more comprehensive automated research path.

## Do not plan around model tuning

The final tunable endpoint, Gemini 1.5 Flash 001, shut down in May 2025. The
API no longer supports tuning on any endpoint.

Batch attribution: `gemini-3.6`, `release-lifecycle`, and
`rolling-2026-08-19`.
