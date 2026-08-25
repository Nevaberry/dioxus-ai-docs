# Serving APIs

Use this reference for compatible request and response behavior, endpoint
capabilities, parsers, speech and embedding APIs, realtime transport, and the
Python, Rust, and gRPC serving paths.

## Core compatible endpoints

### Reranking, scoring, transcription, and Responses (`0.7-0.10`)

The server supports Jina- and Cohere-compatible reranking, `/score` for
embedding models, streaming transcription, and the Responses API. The request
`model` field is optional.

Requests can set `return_tokens_as_token_id` and pass image embeddings. The V1
sampler supports `allowed_token_ids`; Chat accepts `mm_processor_kwargs`; and
requests pass through `bad_words`. Audio longer than 30 seconds is chunked.

`LLM.chat` accepts `chat_template_kwargs`. Embeddings support truncation and
`tokenization_kwargs`, and response usage may report `cached_tokens`.

### Structured output, reasoning, and tools (`0.7-0.10`)

V1 supports structured and reasoning output with backend-specific guided
decoding. `--enable-reasoning` was deprecated. Structured output works with
thinking and speculative decoding; XGrammar supports `tool_choice: required`,
Guidance supports structural tags, and tool calling supports required choice
and `$defs`.

### Responses and tool maturity (`0.11-0.14`)

Responses supports MCP tools, multi-turn non-Harmony requests, reasoning-item
input, parsed tool arguments, `parallel_tool_calls`, tool filtering,
Browser/Container MCP tools, extra body parameters, and MCP streaming.

Chat accepts `reasoning_effort` and the server supports
`--default-chat-template-kwargs`. Parser coverage includes SeedOSS,
Qwen3-Coder XML, DeepSeek-V3.2, Gigachat 3, Holo2, FunctionGemma, and GLM-4.7.

### Retrieval and cancellation (`engine-and-openai-server`)

Create a response at `/v1/responses`, retrieve it at
`/v1/responses/{response_id}`, and cancel it at
`/v1/responses/{response_id}/cancel`.

## Compatibility constraints

### Explicit omissions (`engine-and-openai-server`)

Completions `suffix` and Chat `image_url.detail` are unsupported. Chat `user`
is accepted but ignored. Setting `parallel_tool_calls=false` guarantees at
most one tool call. The default `true` only permits multiple calls; the model
still decides whether to emit them.

### Request validation (`0.23-0.26`)

The server rejects out-of-vocabulary token IDs, non-positive parallel and
scheduling values, non-finite temperature and repetition penalties,
degenerate structured-output settings, and request-level GPU video-backend
selection. Invalid image URLs produce HTTP 422. Regex and derender operations
are resource bounded.

## Embeddings, scoring, and speech

### Embedding and transcription formats (`0.11-0.14`)

Whisper supports `verbose_json` and timestamps. Embedding responses support
`encoding_format=bytes_only`, multiple images or audio items in one request,
and `continue_final_message` on `/embeddings`.

### Speech batch and detection paths (`0.15-0.18`)

Whisper `verbose_json` segments expose `avg_logprob` and `compression_ratio`.
Speech APIs support batch transcription and translation, automatic language
detection, and beam search for offline and online transcription.

### Sparse, late-interaction, and compatible embedding APIs (`0.15-0.18`)

BGE-M3 sparse and ColBERT embeddings are supported. `/score` accepts either
`data_1`/`data_2` or `queries`/`documents`. Sparse-embedding IO processing,
multimodal late-interaction scoring, and Cohere Embed v2 compatibility were
also added.

### Batch chat and mixed embeddings (`0.19-0.22`)

`/v1/chat/completions/batch` provides batch chat. One call can request multiple
embedding types. RLHF integrations can bracket weight changes with explicit
`/start_weight_update` and `/finish_weight_update` calls.

### Message inputs and token metadata (`0.23-0.26`)

`/v1/embeddings` accepts messages and `chat_template_kwargs`. Python-backed
endpoints expose `logprob_token_ids`, while `/v1/completions` accepts
`bad_words`.

## Realtime, render, and streaming

### WebSocket realtime audio (`0.15-0.18`)

The WebSocket Realtime API supports streaming audio with Voxtral realtime and
Qwen3-ASR.

### GPU-less rendering (`0.15-0.18`)

Prompt-preprocessing render endpoints can separate rendering from GPU
inference. `vllm launch render` runs a GPU-less preprocessing/render service.

### Responses streaming growth (`0.15-0.18`)

Responses supports partial-message generation, `include_stop_str_in_output`,
`prompt_cache_key`, sampling parameters, and returned token IDs. It also
supports structured output, streamed reasoning-part events, and streamed tool
and function calls.

### Messages-compatible thinking (`0.15-0.18`)

The messages-compatible API supports thinking blocks, token counting,
`tool_choice=none`, and redacted thinking blocks.

## Request controls, tools, and parsers

### Responses and Completions controls (`0.19-0.22`)

Streamed required and named tool choices, `system_fingerprint`, and
`prompt_embeds` content parts are supported. Responses accepts
`chat_template_kwargs`; endpoint truncation side is configurable; Completions
accepts `thinking_token_budget`; and `reasoning_effort` maps to
`enable_thinking`.

### Unified streaming parser (`0.23-0.26`)

Reasoning and tool calls share `Parser.parse`. The Streaming Parser Engine
supports Qwen3, MiniMax-M2, Nemotron V3, Kimi K2.5-K2.7, Seed-OSS, and DeepSeek
V4. Strict tool calling works in Chat Completions and Responses.

### Namespace tools and timing (`0.23-0.26`)

Responses supports namespace tools, per-request timing metrics, and
`return_loss_mask`. Messages-compatible requests support structured output,
effort, and system-role messages inside the message array, report cache usage,
and accept system messages mid-conversation.

### Endpoint plugins and RLHF controls (`0.23-0.26`)

An endpoint-plugin framework allows serving extensions. The RLHF development
router exposes `/abort_requests`.

### Structured speculation boundary (`0.27.1`)

With speculative decoding, the structured-output grammar advances across the
reasoning-to-final-output boundary instead of losing grammar state there.

## Alternative frontends and transports

### Binary HTTP/2 server (`0.11-0.14`)

A gRPC entrypoint provides binary protocol transport and HTTP/2 multiplexing
as an alternative to REST.

### Experimental Rust frontend (`0.19-0.22`)

The in-tree Rust frontend integrates with data-parallel serving. API-key
authorization extends to `/v2` endpoints.

### Rust serving surface (`0.23-0.26`)

The Rust frontend supports streaming `generate`, dynamic LoRA endpoints,
`/server_info`, and `--enable-request-id-headers`. It adds API-key auth, CORS,
`/pause`, `/resume`, `/is_paused`, `/get_world_size`, static HTTPS, and mTLS for
HTTP and gRPC. Video, audio, native benchmarking, and TorchCodec video decoding
are supported.

The gRPC interface is documented as insecure and private-use only. Keep it on
a trusted network even when a frontend exposes TLS or mTLS.

### Rust control plane (`0.27.1`)

The Rust gRPC control plane exposes engine-aware health, abort, server and
model discovery, and KV-event-source discovery.
