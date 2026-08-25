# Serving APIs, Operations, and Security

## OpenAI-compatible generation and tools

### Endpoint surface

Batch `0.7-0.10` added Jina- and Cohere-compatible reranking, `/score` for
embedding models, streaming transcription, and a Responses API. The request
`model` field became optional. The server also added `/load`, `/is_sleeping`,
SSL key rotation, and `get_tokenizer_info` for tokenizer and chat-template
inspection.

Responses matured in `0.11-0.14` with MCP tools, multi-turn non-Harmony
requests, reasoning-item input, parsed tool arguments,
`parallel_tool_calls` compliance, tool filtering, Browser/Container MCP tools,
extra body parameters, and MCP streaming.

The Responses surface added partial-message generation,
`include_stop_str_in_output`, and `prompt_cache_key`; then sampling parameters
and returned token IDs; then structured output and streamed reasoning-part
events; and finally streaming tool/function calls (`0.15-0.18`).

Batch `0.19-0.22` added `/v1/chat/completions/batch`, allowed multiple
embedding types in one call, and added streamed required or named tool
choices, `system_fingerprint`, and `prompt_embeds` content parts. Responses
gained `chat_template_kwargs`, endpoint truncation side became configurable,
Completions gained `thinking_token_budget`, and `reasoning_effort` mapped to
`enable_thinking`.

Batch `0.23-0.26` added Responses namespace tools, per-request timing metrics,
and `return_loss_mask`. `/v1/embeddings` accepts messages plus
`chat_template_kwargs`; `/v1/completions` accepts `bad_words`; Python-backed
endpoints expose `logprob_token_ids`.

### Explicit compatibility omissions

The Completions `suffix` field and Chat `image_url.detail` are unsupported.
Chat's `user` field is accepted but ignored. `parallel_tool_calls=false`
guarantees at most one tool call; the default `true` allows multiple calls but
does not guarantee them because output remains model-dependent.

Responses are created at `/v1/responses`, retrieved from
`/v1/responses/{response_id}`, and cancelled at
`/v1/responses/{response_id}/cancel`.

### Structured output, reasoning, and tool parsing

V1 gained structured outputs and reasoning output in `0.7-0.10`, including
backend-specific guided-decoding options. `--enable-reasoning` was later
deprecated. Structured output became compatible with thinking and speculative
decoding; XGrammar gained `tool_choice: required`, Guidance gained structural
tags, and tool calling added required choice plus `$defs`.

Parser support expanded in `0.11-0.14`: SeedOSS and Qwen3-Coder XML,
DeepSeek-V3.2, Gigachat 3, Holo2, FunctionGemma, and GLM-4.7. Chat gained the
`reasoning_effort` request parameter and `--default-chat-template-kwargs`.

Batch `0.23-0.26` unified reasoning and tool-call parsing behind
`Parser.parse`, then added the Streaming Parser Engine and Qwen3,
MiniMax-M2, Nemotron V3, Kimi K2.5-K2.7, Seed-OSS, and DeepSeek V4 parsers.
Strict tool calling works in Chat Completions and Responses for supported
parsers.

## Request inputs, tokens, and multimodal content

### Token and multimodal controls

Batch `0.7-0.10` added `return_tokens_as_token_id`, image embeddings as input,
V1 `allowed_token_ids`, Chat `mm_processor_kwargs`, `bad_words` passthrough,
and chunking for audio longer than 30 seconds. `LLM.chat` gained
`chat_template_kwargs`; embedding requests gained truncation control and then
`tokenization_kwargs`; usage can report `cached_tokens`.

Embedding formats in `0.11-0.14` added `encoding_format=bytes_only`, multiple
images or audio items per request, and `continue_final_message` on
`/embeddings`. Whisper added `verbose_json` plus timestamp output.

### Generation and sampling request controls

Responses sampling parameters and token-ID returns arrived in
`0.15-0.18`. From that batch onward, `generation_config.max_tokens` supplies a
default rather than a hard ceiling, so a request can explicitly exceed it.
Newer speculative paths reject unsupported sampling parameters rather than
silently ignoring them.

### Validation hardening

Across `0.23-0.26`, serving rejects out-of-vocabulary token IDs, non-positive
parallel or scheduling knobs, non-finite temperature or repetition penalties,
degenerate structured-output configurations, and request-level GPU
video-backend selection. Invalid image URLs return HTTP 422. Regex and
derender processing have resource bounds.

## Embedding, scoring, and speech APIs

### Embeddings and scoring

Batch `0.15-0.18` added BGE-M3 sparse and ColBERT embeddings and let `/score`
accept either `data_1`/`data_2` or `queries`/`documents`. Later entries in the
same batch added sparse-embedding IO processing, multimodal late-interaction
scoring, and Cohere Embed v2 compatibility.

Multi-task pooling support lets one model advertise multiple tasks and
poolers, selecting pooling parameters dynamically rather than assuming a
single fixed task/pooler (`0.7-0.10`). Later endpoint work allows multiple
embedding types in one call and message-form embedding input.

### Transcription and realtime audio

Whisper `verbose_json` segments expose `avg_logprob` and `compression_ratio`.
Batch transcription and translation, automatic language detection, and beam
search for offline and online transcription followed in `0.15-0.18`.

That batch also added a WebSocket Realtime API on Voxtral infrastructure and
extended realtime streaming to Qwen3-ASR. Audio embeddings are accepted in
Chat Completions. The Transformers modeling backend later gained audio-model
support (`0.27.1`).

## Anthropic-compatible messages

Thinking blocks, token counting, and `tool_choice=none` arrived in
`0.15-0.18`; redacted thinking blocks were accepted later in the same batch.
Batch `0.23-0.26` added structured output, effort, and system-role messages
inside the messages array, reported cache usage, and handled system messages
that appear mid-conversation.

## Rendering and extensibility

Prompt-preprocessing render endpoints appeared in `0.15-0.18`, followed by
`vllm launch render` for a GPU-less preprocessing and rendering service.

An endpoint-plugin framework and `/abort_requests` on the RLHF development API
router arrived in `0.23-0.26`. Treat plugin endpoints as part of the selected
frontend's deployment contract, including authentication and validation.

## Python, Rust, and gRPC frontends

### Rust frontend rollout

An experimental in-tree Rust frontend arrived in `0.19-0.22` with
data-parallel integration; API-key authorization covers `/v2` endpoints.

Batch `0.23-0.26` added streaming `generate`, dynamic LoRA endpoints,
`/server_info`, and `--enable-request-id-headers`; then API-key auth, CORS,
`/pause`, `/resume`, `/is_paused`, and `/get_world_size`; then static HTTPS and
mTLS for HTTP and gRPC; and finally video, audio, and native `vllm-bench`.
TorchCodec became a video-decoding backend during that rollout.

In `0.27.1`, the Rust gRPC control plane gained engine-aware health, abort
control, server and model discovery, and KV-event-source discovery.
`vllm-bench` is integrated into the `vllm` CLI.

### gRPC deployment boundary

A binary HTTP/2-multiplexed gRPC server was added in `0.11-0.14` as an
alternative to REST. Despite later TLS and mTLS support in the Rust frontend,
the `0.23-0.26` notes explicitly describe gRPC as insecure and suitable only
for private use. Do not expose it solely because transport configuration is
available.

## Operations and observability

### Health and state endpoints

From `0.11-0.14`, health returns HTTP 503 when the engine is dead.
`/reset_prefix_cache` can reset KV connectors, and `/server_info` exposes
environment information. Earlier endpoints include `/load`, `/is_sleeping`,
and tokenizer information; Rust adds pause/resume and world-size controls.

Batch `0.15-0.18` can derive `api_server_count` from data-parallel size and
adds `--ssl-ciphers`, nested YAML configuration,
`--disable-access-log-for-endpoints`, and clearing of multimodal and encoder
caches. It later adds `--distributed-timeout-seconds` plus graceful-shutdown
timeout handling for in-flight requests. Batch `0.19-0.22` adds
`VLLM_MAX_N_SEQUENCES`, opt-in media URL caching through `VLLM_MEDIA_CACHE`,
`VLLM_SKIP_MODEL_NAME_VALIDATION`, and `--cpu-distributed-timeout-seconds`.

### Request and engine logs

`--enable-log-requests` logs request IDs, parameters, and LoRA requests at
INFO; at DEBUG it also logs prompt text or token IDs. `VLLM_LOGGING_LEVEL`
selects the threshold. `--aggregate-engine-logging` reports aggregate rather
than per-engine data-parallel statistics. `--fail-on-environ-validation`
makes environment-validation failures fatal.

### Metrics migration

The `0.7-0.10` metrics `vllm:time_in_queue_requests`,
`vllm:model_forward_time_milliseconds`, and
`vllm:model_execute_time_milliseconds` were deprecated.
`--show-hidden-metrics-for-version` supports transition periods. Later
additions include `vllm:cache_config_info`, KV-event publishing, and access to
in-memory Prometheus metrics; non-GPU-specific metrics deprecated their `gpu_`
prefixes.

Batch `0.15-0.18` removed `vllm:time_per_output_token_seconds` in favor of
`vllm:inter_token_latency_seconds`. Do not retain dashboards that silently mix
old and replacement semantics.

## Caching and serialization security

Prefix-cache salting and `VLLM_ALLOW_INSECURE_SERIALIZATION` arrived in
`0.7-0.10`, along with a V1 option to disable pickle fallback. Completions and
Responses can carry `cache_salt`; reproducible prefix-cache hashes can use
SHA-256 plus CBOR.

Batch `0.11-0.14` addressed GHSA-wr9h-g72x-mwhm and CVE-2025-62164. It also
prevented tokens from leaking through crash logs, loaded PyTorch weights with
`weights_only=True`, and corrected invalid UTF-8 handling, CPU RoPE output
under `--enforce-eager`, tool-call streaming completion, stuck CPU scheduling
after encoder-cache leaks, tools-plus-`response_format` crashes, and Voxtral
transcription.

Batch `0.15-0.18` made NemotronVL and KimiK25 honor `trust_remote_code` and
gated RLHF weight-sync deserialization behind the insecure-serialization
setting. Keep that gate closed unless the payload source and execution path are
trusted.

## Operational troubleshooting

- If a health probe returns 503, diagnose engine death instead of increasing
  probe tolerance.
- If request logging may contain prompts, keep DEBUG output away from broadly
  accessible log sinks.
- If tools stream incorrectly, confirm the parser, strict-tool setting,
  frontend, and whether the request uses Responses or Chat Completions.
- If embedding or speech input is rejected, verify endpoint-specific content
  formats and versioned support for bytes, multiple media items, timestamps,
  or messages.
- If gRPC is required across hosts, treat private routing, authorization, TLS,
  and application-layer trust as separate controls.
