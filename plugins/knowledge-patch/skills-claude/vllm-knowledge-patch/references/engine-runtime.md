# Engine, Runtime, and Configuration

## V1 architecture and runner selection

### EngineCore and token-based scheduling

V1 isolates the scheduler and model executor in `EngineCore`. Tokenization,
multimodal preprocessing, detokenization, and response streaming overlap
outside that hot path. Workers cache request state and receive incremental
updates, so single-GPU and tensor-parallel execution share a symmetric worker
design.

Scheduling is token-based, not split into separate prefill and decode phases.
Each step is conceptually an allocation such as `{request_id: num_tokens}`;
the same budget covers ordinary decoding, chunked prefill, prefix caching, and
speculative decoding.

### V1 replaced V0

In batch `0.7-0.10`, V1 moved from opt-in via `VLLM_USE_V1=1` to the default
for supported use cases. `VLLM_USE_V1=0` was a temporary escape hatch. The
cleanup removed V0 CPU, XPU, TPU, and HPU backends, long-context LoRA,
Phi3-Small and BlockSparse Attention, and speculative-decoding workers.

Batch `0.11-0.14` completed removal of `AsyncLLMEngine`, `LLMEngine`,
`MQLLMEngine`, the V0 attention backends and executors, and the remaining V0
interfaces. V1 is the only engine. Custom model `forward` methods no longer
receive `kv_cache` or `attn_metadata`; attention backends obtain them from
`forward_context`. The temporary `SupportsV0Only` protocol was only useful
while V0 still existed.

### Model Runner V2 rollout

Model Runner V2 first appeared as an experimental, disabled-by-default GPU
runner in `0.11-0.14`, with M-RoPE, `logit_bias`, `allowed_token_ids`, and
`min_tokens` added by the end of that batch. In `0.15-0.18` it expanded to
VLMs, pipeline and decode-context parallelism, piecewise and mixed CUDA-graph
capture, pooling models, Whisper state, and probabilistic rejection sampling.

In `0.19-0.22`, MRV2 added EPLB, multimodal speculative embeddings,
greedy/logprob rejection modes, multiple prompt logprobs, and Qwen3.5/Mamba
hybrid support. It became the default for dense Qwen3, with automatic fallback
to MRV1 for unsupported features. Batch `0.23-0.26` extended the default path
to dense Llama and Mistral, then quantized models, and finally every dense
model. That batch also removed legacy PagedAttention and added EVS,
Mamba-hybrid prefix caching, and dynamic speculation under full CUDA graphs.

In `0.27.1`, MRV2 gained encoder-only attention, sequence pooling for
embeddings and classification, encoder token classification and embeddings,
BGE-M3 pooling, multimodal CPU execution, and a multi-layer MTP speculator;
PCP now selects MRV2.

## Compilation, graphs, and scheduling

### Compilation modes

V1 integrates `torch.compile` and enables it by default; `-O3` explicitly
selects it in the early interface. Batch `0.11-0.14` made
`FULL_AND_PIECEWISE` the default CUDA-graph mode and disabled standalone
Inductor compilation. Startup tradeoffs became `-O0` through `-O3`, selective
compilation became available through `compile_ranges`, and deprecated
`-O.xx` spellings were removed.

### Async scheduling evolution

The `--async-scheduling` option was experimental in `0.7-0.10`, overlapping
engine-core scheduling with the GPU runner. In 0.10.2 and early
`0.11-0.14`, it could corrupt output under preemption and some other cases.
It later became default except with pipeline parallelism, CPU, and speculative
decoding other than MTP/Eagle; `--no-async-scheduling` opts out.

Batch `0.15-0.18` made async scheduling compatible and then fully supported
with pipeline parallelism. N-gram speculative decoding also became compatible
with it. Continue to check the selected backend and speculative method rather
than treating one historical compatibility matrix as universal.

### Performance and attention presets

`--performance-mode {balanced,interactivity,throughput}` provides coarse
deployment tuning, and `--attention-backend auto` chooses a backend
automatically (`0.15-0.18`). On Blackwell, MLA initially defaulted to
FlashInfer and prefill to TRTLLM; later, cascade attention became disabled by
default. Sparse MLA FP8-KV later defaulted to FlashInfer, CPU enabled
`tcmalloc`, FlashAttention 4 became the MLA prefill default on SM90+, and
RayExecutorV2 plus the FlashInfer top-k/top-p sampler became defaults
(`0.19-0.22`).

Attention backends can vary by KV-cache group (`0.23-0.26`), and
sliding-window support is now an explicit backend capability. This permits
mixed-backend hybrid models.

## Batching, context, and prefix caching

### Prefix-cache behavior

V1 keeps hash-based prefix lookup and LRU eviction, but uses constant-time
eviction and low allocation overhead. Prefix caching is therefore enabled by
default for supported non-hybrid models even when hit rates are low.

Hybrid models keep prefix caching opt-in, while chunked prefill follows the
model's support declaration. Disabling chunked prefill on a supported
generation model, or enabling it on an unsupported pooling model, can crash or
corrupt output. RISC-V CPU execution forces both chunked prefill and prefix
caching off.

Mamba and hybrid models can use block-aligned states with
`--enable-prefix-caching --mamba-cache-mode align`; speculative decoding later
became compatible with that mode (`0.15-0.18`).

### Automatic context fitting

`--max-model-len auto` selects a context length that fits available GPU memory
(`0.11-0.14`). Set `VLLM_LOG_MODEL_INSPECTION=1` or print an `LLM` object to
inspect modules, attention backends, and quantization.

Without chunked prefill, an unspecified batched-token limit is raised to at
least the model context length. A multimodal prefix-LM can raise it again to
fit its largest single media item. The result is capped at
`max_num_seqs × max_model_len`, and an unspecified sequence limit is capped at
the final batched-token count.

### Hardware-dependent scheduler defaults

GPUs with at least 70 GiB except A100 default to 16,384/8,192 batched tokens
for offline/server use and 1,024 sequences; other GPUs use 8,192/2,048 tokens
and 256 sequences. CPU defaults are 4,096/256 offline and 2,048/128 server,
multiplied by `PP × TP`. TPU V6E, V5E, and V5P token defaults are respectively
2,048/1,024, 1,024/512, and 512/256 offline/server. Throughput mode doubles
token or sequence defaults that were not explicitly overridden.

## Sampling and returned probabilities

### Seed and top-k semantics

The default seed became `None` in 0.8, then V1 changed it to `0` in 0.9. This
makes separate runs deterministic even with nonzero temperature. Caller RNG
isolation does not apply when `VLLM_USE_V1_MULTIPROCESSING=0`. From 0.9,
`top_k=0` disables top-k sampling; `-1` remains only a temporary compatibility
sentinel.

Later, flat-logprob control moved from an environment variable into
`SamplingParams`, `seed=None` was deprecated, and `seed_everything` was also
deprecated (`0.11-0.14`). Unsupported speculative-decoding sampling parameters
are rejected instead of silently ignored.

### Generation configuration defaults

Starting in 0.8, a model's `generation_config` supplies chat-template and
sampling defaults such as temperature. Make these values explicit when an
upgrade or model change must not alter an unchanged request. From
`0.15-0.18`, `generation_config.max_tokens` is a default rather than a hard
ceiling, so an explicit request value can exceed it.

### Logprob behavior

Prompt logprobs are returned for every token and `logprobs=-1` requests the
full vocabulary (`0.11-0.14`). A separate runtime logprobs mode selects which
processing stage supplies returned logprobs. Generation models can retain
`lm_head` in FP32 through `head_dtype`, including through the LoRA path
(`0.23-0.26`).

## Configuration and launch semantics

### Nested values and readable sizes

Dataclass-backed options accept either a whole JSON object or dotted keys such
as `--attention-config.flash_attn_version=2`. Bare values inside configuration
JSON accept decimal `k/m/g/t` and binary `K/M/G/T` suffixes, for example:

```bash
vllm serve MODEL --kv-transfer-config '{"cpu_bytes_to_use":80m}'
```

Human-readable integers also work for batch-token, scheduled-token, KV-memory,
and safetensors-prefetch block sizes. Nested YAML configuration was added in
`0.15-0.18`.

### Attention configuration migration

`VLLM_ATTENTION_BACKEND` was replaced with `--attention-backend` and
`AttentionConfig` (`0.11-0.14`); `LLM` also accepts `attention_config`.
Backend environment variables later gained `--moe-backend` and
`--linear-backend` replacements (`0.19-0.22`).

### Device placement

From `0.23-0.26`, vLLM does not mutate `CUDA_VISIBLE_DEVICES`; use the
`device_ids` argument. ROCm also began deprecating `CUDA_VISIBLE_DEVICES`.
With an existing visibility mask, integer `--device-ids` index that visible
list instead of raw physical devices. UUIDs are allowed, but cannot be mixed
with integers; duplicates are rejected. The option does not affect Ray
executors.

### Offline repository resolution and tokenizer skipping

In Hugging Face offline mode, non-cloud model and tokenizer repository IDs are
replaced by revision-resolved local paths. Cloud-storage URIs remain unchanged.
`EngineArgs(tokens_only=True)` independently skips tokenizer initialization.

### CLI usability

The consolidated `vllm bench` command replaced separate benchmark entrypoints,
and `--dataset` in `benchmark_serving.py` was deprecated (`0.7-0.10`). Paged
help is available with `--help=page`; the CLI default model changed to
Qwen3-0.6B. The Rust `vllm-bench` later became integrated into the `vllm` CLI
(`0.27.1`).

## Removed and deprecated runtime interfaces

Batch `0.11-0.14` removed `num_lookahead_slots`, `best_of`, LoRA extra
vocabulary, deprecated plugin/compilation/task/seed/multimodal settings,
`embed_input_ids` and `embed_multimodal` fallbacks, and the tokenizer setter.
`--convert reward` became `--convert embed`, and the `xformers` backend was
deprecated.

Direct-child EPLB fields on `ParallelConfig`, `guided_*`,
`override_pooler_config`, `disable_log_requests`,
`CompilationConfig.use_inductor`, and already-deprecated metrics were also
scheduled for removal. Batch `0.15-0.18` removed per-request logits
processors and `swap_space`, along with other format- and metrics-specific
removals documented in their topic references.

Batch `0.19-0.22` deprecated `--calculate-kv-scales`, the `score` task,
virtual engines, and `--disable-frontend-multiprocessing`. It removed old
import locations for `get_tokenizer` and `resolve_hf_chat_template`, plus
deprecated MLA-prefill arguments. Batch `0.23-0.26` moved legacy
`api_server.py` into examples and deleted legacy PagedAttention.

## Container startup checks

As of `0.27.1`, vLLM respects cgroup memory limits on every platform and fails
fast when `/dev/shm` is too small. This changes startup behavior in constrained
containers; size shared memory and container memory explicitly.
