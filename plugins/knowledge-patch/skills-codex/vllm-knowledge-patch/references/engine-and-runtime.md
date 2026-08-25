# Engine and Runtime

Use this reference for engine architecture, scheduler behavior, compilation,
attention selection, sampling defaults, lifecycle controls, and local runtime
configuration.

## V1 architecture and batching

### EngineCore isolates the hot path (`v1-architecture-and-batching`)

V1 places the scheduler and model executor in an isolated `EngineCore`.
Tokenization, multimodal preprocessing, detokenization, and response streaming
can overlap outside the core. Workers cache request state and receive
incremental updates, giving single-GPU and tensor-parallel execution the same
symmetric worker design.

### Scheduling is token-based (`v1-architecture-and-batching`)

V1 does not represent prefill and decode as separate scheduling phases. Each
step allocates work conceptually as `{request_id: num_tokens}`. One token
budget therefore covers ordinary decode, chunked prefill, prefix caching, and
speculative decoding.

### Prefix and multimodal reuse (`v1-architecture-and-batching`)

Prefix caching retains hash lookup and LRU eviction but uses constant-time
eviction and low-overhead allocation, so it remains cheap even without hits
and is enabled by default. Multimodal preprocessing happens outside the engine
loop and can be shared across requests. Image hashes participate in prefix
lookup, while a distinct encoder cache retains vision embeddings so text
prefill can be split across scheduler steps.

## Compilation, graphs, and scheduling

### Compilation and early async scheduling (`0.7-0.10`)

V1 fully integrates `torch.compile` and enables it by default; `-O3` requests
it explicitly. `--async-scheduling` was introduced experimentally to overlap
engine-core scheduling with the GPU runner.

### Graph defaults and selective compilation (`0.11-0.14`)

`FULL_AND_PIECEWISE` became the default CUDA graph mode and standalone
Inductor compilation was disabled. Use `-O0` through `-O3` for startup versus
runtime tradeoffs and `compile_ranges` for selective compilation; the old
`-O.xx` form was removed.

Async scheduling can corrupt output in 0.11 and 0.10.2 under preemption and
some other cases. It became enabled by default in 0.14 except for pipeline
parallelism, CPU, and speculative methods other than MTP/Eagle. Use
`--no-async-scheduling` to opt out.

### Pipeline and speculative combinations (`0.15-0.18`)

Async scheduling became compatible, then fully supported, with pipeline
parallelism. It can also run with GPU NGram speculation. Model Runner V2 added
piecewise and mixed CUDA-graph capture.

### Zero-bubble speculative overlap (`0.19-0.22`)

Async scheduling and speculative decoding can run together with zero-bubble
overlap.

## Model Runner V2

### Experimental introduction (`0.11-0.14`)

The experimental GPU Model Runner V2 is disabled by default. Its early support
includes M-RoPE, `logit_bias`, `allowed_token_ids`, and `min_tokens`.

### Workload expansion (`0.15-0.18`)

MRV2 added vision-language models, pipeline and decode-context parallelism,
piecewise and mixed graph capture, pooling models, Whisper state, and
probabilistic rejection sampling.

### Selective defaulting (`0.19-0.22`)

MRV2 added EPLB, multimodal speculative embeddings, greedy and logprob modes
for rejection sampling, multiple prompt logprobs, and Qwen3.5/Mamba hybrid
support. It became the default for dense Qwen3 models, with automatic fallback
to MRV1 if a requested feature is unsupported.

### Dense-model takeover (`0.23-0.26`)

MRV2 became the default first for dense Llama and Mistral, then quantized
models, then every dense model. The legacy PagedAttention implementation was
deleted. MRV2 gained EVS, Mamba-hybrid prefix caching, and dynamic speculation
under full CUDA graphs.

### Encoder, pooling, and CPU multimodal paths (`0.27.1`)

MRV2 covers encoder-only attention, sequence pooling for embeddings and
classification, encoder token classification and embeddings, BGE-M3 pooling,
CPU multimodal execution, and a multi-layer MTP speculator. PCP selects MRV2.

## Sampling, generation, and log probabilities

### Defaults and sentinels (`0.7-0.10`)

The seed default moved from `None` to V1's `0`, making separate runs
deterministic even with nonzero temperature. Caller RNG isolation does not
apply with `VLLM_USE_V1_MULTIPROCESSING=0`. `top_k=0` disables top-k sampling;
`-1` was temporarily accepted.

A model's `generation_config` supplies chat-template and sampling defaults,
including temperature. Pin those request fields to prevent upgrades or model
changes from silently changing behavior.

### Prompt logprobs and stricter validation (`0.11-0.14`)

Prompt logprobs are returned for every token and `logprobs=-1` requests the
full vocabulary. Flat-logprob control moved from an environment variable into
`SamplingParams`, and `seed=None` was deprecated. Unsupported speculative
sampling parameters are rejected instead of ignored.

### Token-limit semantics (`0.15-0.18`)

`generation_config.max_tokens` supplies a default rather than a hard ceiling;
an explicit request value can exceed it.

### Diffusion sampling (`0.27.1`)

DiffusionGemma accepts both `top_k` and `top_p`.

## Runtime control and post-training

### Lifecycle APIs (`0.7-0.10`)

`LLM.sleep`, `LLM.wake_up`, `LLM.collective_rpc`, and
`LLM.reset_prefix_cache` support post-training integrations. The RPC surface
also supports runtime weight reload and configuration update. A logprobs mode
chooses which processing stage supplies returned logprobs.

### Input, state, and model application (`0.11-0.14`)

V1 supports CPU KV-cache offload with LRU management, prompt embeddings,
sharded state loading, and `LLM.apply_model`. Asynchronous RL workflows can
pause and resume generation. Chat completions accept audio embeddings.

### Streaming input and weight synchronization (`0.15-0.18`)

Engines accept async generators of `StreamingInput` while preserving KV-cache
alignment, enabling session-oriented workloads such as speech recognition.
RLHF paths gained native NCCL weight synchronization, layerwise reload, and
pause/resume that preserves requests, followed by IPC synchronization and
sleep level 0 with an enqueue/wait pattern.

### Versioned rollout state (`0.27.1`)

RL rollouts can tag weights with a version. The FlashInfer monolithic MoE
kernel can return router-replay output for training integrations.

## Attention, prefix caching, and offload

### Attention configuration (`0.11-0.14`)

Use `--attention-backend` and `AttentionConfig` instead of
`VLLM_ATTENTION_BACKEND`; `LLM` also accepts `attention_config`.

### Hybrid prefix alignment and hardware defaults (`0.15-0.18`)

Mamba and hybrid models can cache block-aligned states with
`--enable-prefix-caching --mamba-cache-mode align`, including speculative
decoding. Blackwell defaults MLA to FlashInfer and prefill to TRTLLM. Cascade
attention is disabled by default. `--attention-backend auto` chooses a backend
automatically.

### Weight and KV offload (`0.15-0.18`)

Weight Offloading V2 can prefetch, selectively offload weights to CPU, and use
pinned copies without doubling CPU memory. KV offload can restrict CPU stores
to frequently reused blocks, use FlexKV, and describe multiple KV groups.
Connector load failures default to `fail`; configure `recompute` explicitly if
transparent recomputation is required.

### Backend defaults (`0.19-0.22`)

FP8-KV sparse MLA defaults to FlashInfer. FlashAttention 4 became the default
MLA prefill backend on SM90+, RayExecutorV2 became default, and the FlashInfer
top-k/top-p sampler became default. CPU enables `tcmalloc` by default.

### Per-cache-group backends (`0.23-0.26`)

Each KV-cache group may select a different attention backend. Sliding-window
support is an explicit backend capability, enabling mixed-backend hybrid
models. Generation models may set `head_dtype` to retain the `lm_head` in FP32;
this also applies through LoRA.

### FlashAttention 4 (`0.27.1`)

On SM100, FlashAttention 4 supports FP8 KV caches and head dimension 256.

## Engine arguments and automatic sizing

### Nested flags and readable sizes (`engine-and-openai-server`)

Dataclass options accept a whole JSON object or dotted keys such as
`--attention-config.flash_attn_version=2`. Bare JSON values accept decimal
lowercase `k/m/g/t` and binary uppercase `K/M/G/T` suffixes. Human-readable
integers also work for batch-token, scheduled-token, KV-memory, and
safetensors-prefetch block sizes.

```bash
vllm serve MODEL --kv-transfer-config '{"cpu_bytes_to_use":80m}'
```

### Scheduler defaults (`engine-and-openai-server`)

On GPUs with at least 70 GiB except A100, offline/server defaults are
16,384/8,192 batched tokens and 1,024 sequences. Other GPUs use
8,192/2,048 tokens and 256 sequences. CPU defaults are 4,096/256 offline and
2,048/128 server, multiplied by `PP × TP`. TPU V6E, V5E, and V5P token defaults
are respectively 2,048/1,024, 1,024/512, and 512/256 offline/server.
Throughput mode doubles token or sequence defaults that were not overridden.

Without chunked prefill, an unspecified token limit rises to at least model
context length; a multimodal prefix-LM can raise it again to fit its largest
single media item. It is capped by `max_num_seqs × max_model_len`; an
unspecified sequence limit is capped by the final token count.

### Context fitting and inspection (`0.11-0.14`)

Use `--max-model-len auto` to select a context length that fits GPU memory. Set
`VLLM_LOG_MODEL_INSPECTION=1` or print an `LLM` object to inspect modules,
attention backends, and quantization.

### Performance presets (`0.15-0.18`)

`--performance-mode {balanced,interactivity,throughput}` applies a coarse
workload preset.

### Hybrid correctness constraints (`engine-and-openai-server`)

Prefix caching defaults on only for a supported, non-hybrid model. Chunked
prefill follows the model's declared support. Disabling chunked prefill on a
supported generation model or enabling it on an unsupported pooling model can
crash or corrupt output. RISC-V CPU forces chunked prefill and prefix caching
off.

### Offline repository resolution (`engine-and-openai-server`)

In Hugging Face offline mode, non-cloud model and tokenizer repository IDs are
resolved to revision-specific local paths; cloud URIs are unchanged.
`EngineArgs(tokens_only=True)` skips tokenizer initialization independently.
