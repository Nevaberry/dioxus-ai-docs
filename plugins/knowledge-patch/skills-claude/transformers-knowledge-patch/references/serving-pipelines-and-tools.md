# Serving, pipelines, and tools

## Command-line chat

### Simplified chat entry point (4.52.1)

Use `transformers chat MODEL`. Generation settings follow the model as
`GenerationConfig`-style `key=value` arguments rather than a fixed flag set.

```bash
transformers chat Qwen/Qwen2.5-0.5B-Instruct do_sample=False max_new_tokens=10
```

## Transformers Serve

### Initial local server (4.54.0)

`transformers serve` is a separate utility intended for experimentation and
private local use across supported modalities. It initially exposes
OpenAI-compatible `/v1/chat/completions`, `/v1/responses`,
`/v1/audio/transcriptions`, and `/v1/models`, letting API clients and
`transformers chat` share the same server.

### Continuous batching integration (4.57.0)

Stable `generate_batch` execution is integrated into the server for full- and
sliding-window models. The documented model-side configuration uses paged SDPA.

### Completion, media, compilation, and tools (5.6.0)

The server adds legacy `/v1/completions`, accepts audio and video, and supports
`--compile` and `--model-timeout`. It forwards `tool_calls` and `tool_call_id`
to processor inputs and uses `parse_response` for tool-call output. A request
whose model differs from the pinned server model receives HTTP 400.

### Schema correction (5.9.0)

`GET /v1/models` returns `owned_by` as a string rather than a list.

## Continuous-batching operations

### Request ordering and media batches (5.1.0)

Incoming request order is preserved. `make_batched_video` accepts
five-dimensional arrays.

### CPU offload and long generations (5.7.0)

Requests can be offloaded to CPU. KV deduplication and memory estimation are
corrected for generations of 16K tokens or more, and per-request sampling
parameters are documented.

### Tensor parallelism and observability (5.9.0)

Continuous batching supports tensor parallelism. Its `generate_batch()` path
restores `_attn_implementation` and uses corrected request offsets. The
continuous-batching OpenTelemetry integration was removed; replace it with
application-level instrumentation if traces are required.

### Capacity and compilation controls (5.15.1)

Use `max_requests_per_batch` to bound a batch. The default compile level is
configurable, and the batcher can select Flash Attention automatically when
appropriate.

## Pipeline changes

### Image-text post-processing (4.50.0)

The `image-text-to-text` pipeline accepts post-processing keyword arguments.

### Pipeline dtype default (4.53.0)

Pipelines default to `dtype="auto"`. Supply an explicit dtype when precision
must not follow the loaded checkpoint.

### Gemma 3n image-text prompts (4.53.0)

The image-text pipeline can receive an image URL and prompt text containing
`<image_soft_token>` for Gemma 3n.

### Batched and custom inference (4.57.0)

Image-text inference supports batch sizes greater than one. Custom generation
implementations can use relative imports, and
`ProcessorMixin.apply_chat_template` correctly loads PIL images.

### Task-name cleanup (5.3.0)

The v5 cleanup removes or changes `question-answering`,
`visual-question-answering`, and `image-to-image`. Update pipeline construction
to the supported replacement task rather than assuming the former name remains
an alias.

## Inspection, visualization, and progress

### Attention layouts (4.50.0)

`AttentionMaskVisualizer` loads a tokenizer and model ID, then displays regular,
sliding-window, and multimodal attention layouts.

### Keypoint matching (4.55.0)

`plot_keypoint_matching` is deprecated. Use
`visualize_keypoint_matching`.

### Whisper progress and timestamps (4.54.0, 4.55.0)

Whisper pipeline word timestamps interpret a timestamp token as the end of its
token span. Transcription accepts a progress-monitoring callback.

### Sam3 video progress (5.1.0)

`Sam3VideoModel` can disable its progress bar.

## Serving validation checklist

- Exercise every enabled endpoint and validate request/response schemas.
- Confirm model-name mismatches return 400 and `owned_by` is a string.
- Test audio/video payloads, tool-call forwarding and parsing, compilation, and
  model timeout behavior.
- Verify request ordering, per-request sampling, CPU offload, and long-context
  capacity under continuous batching.
- Replace any dependency on removed continuous-batching telemetry.
