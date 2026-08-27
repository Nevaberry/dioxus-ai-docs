# Operations and Migrations

Use this reference for upgrade planning, runtime packaging, observability,
security, process controls, and retired interfaces.

## Engine and configuration migrations

### V1 replaced V0 (`0.7-0.10`)

V1 was opt-in with `VLLM_USE_V1=1`, became the default for supported use
cases, and retained `VLLM_USE_V1=0` only while V0 remained available. The V0
CPU, XPU, TPU, and HPU backends were removed together with long-context LoRA,
Phi3-Small, BlockSparse Attention, and speculative-decoding workers.

### V0 interfaces were deleted (`0.11-0.14`)

V1 is the only engine. `AsyncLLMEngine`, `LLMEngine`, `MQLLMEngine`, V0
attention backends and executors, and all remaining V0 interfaces were removed.
Also removed were `num_lookahead_slots`, `best_of`, LoRA extra vocabulary,
deprecated plugin/compilation/task/seed/multimodal settings,
`embed_input_ids`/`embed_multimodal` fallbacks, and the tokenizer setter.
Replace `--convert reward` with `--convert embed`.

The `xformers` backend, `seed_everything`, direct-child EPLB fields on
`ParallelConfig`, `guided_*`, `override_pooler_config`,
`disable_log_requests`, `CompilationConfig.use_inductor`, and legacy metrics
were deprecated in this period.

### More legacy paths were retired (`0.15-0.18`)

`vllm:time_per_output_token_seconds` was replaced by
`vllm:inter_token_latency_seconds`. DeepSpeedFp8, RTN, BitBlas, Marlin 24,
`reasoning_content`, `VLLM_ALL2ALL_BACKEND`, per-request logits processors,
and `swap_space` were removed.

### Backend and import migrations (`0.19-0.22`)

`--calculate-kv-scales`, the `score` task, virtual engines, and
`--disable-frontend-multiprocessing` were deprecated. Per-tensor/per-channel
FP8 and Sparse24 integration were removed. Old import locations for
`get_tokenizer` and `resolve_hf_chat_template` and deprecated MLA-prefill
arguments were removed. Replace backend environment variables with
`--moe-backend` and `--linear-backend`.

### Placement and retired integrations (`0.23-0.26`)

The runtime no longer mutates `CUDA_VISIBLE_DEVICES`; use `device_ids` for
explicit placement. ROCm also began deprecating `CUDA_VISIBLE_DEVICES`.
`JAISLMHeadModel` and NIXL's `kv_both` role were deprecated. ERNIE, Xverse,
Bamba, the InternLM registry alias, `P2pNcclConnector`, Baichuan, Aquila,
Tarsier, Tarsier2, Mantis, TeleChat, Persimmon, and Fuyu were removed;
first-generation Qwen/QwenVL were deprecated. `gptq_marlin` was dropped on
ROCm, legacy `api_server.py` moved to examples, and the old online FP8 MoE
class was deprecated.

## Runtime and packaging transitions

### Wheel progression (`0.7-0.10`)

The runtime moved through PyTorch 2.6 with CUDA 12.4 wheels, then PyTorch 2.7
with CUDA 12.8 as the default. CUDA 12.4 support was removed, a CUDA 12.6
artifact was published separately, and `--torch-backend=auto` supported the
CUDA 12.8 install flow. The later runtime uses PyTorch 2.7.1.

### CUDA, ROCm, CPU, and Transformers requirements (`0.11-0.14`)

CPU builds moved to PyTorch 2.8 and ROCm to 7.0. Later packages require
PyTorch 2.9.0 with CUDA 12.9 and Transformers 4.57.3, then PyTorch 2.9.1 with a
default `cu129` wheel.

### Optional executors and renamed packages (`0.15-0.18`)

PyTorch moved to 2.10.0; use the updated wheel that fixes the CUDA 12.9+
library mismatch. XPU moved from IPEX to `vllm-xpu-kernels`, ROCm renamed
`aiter` to `amd-aiter`, and Ray stopped being a default dependency, so install
it explicitly when selected.

### Modern compiler and image baseline (`0.19-0.22`)

Default package and compatible-server images moved to CUDA 13.0; CUDA and XPU
builds moved to PyTorch 2.11. Python 3.14 and `transformers>=5` became
supported, Transformers v4 was deprecated, and builds require a C++20
compiler. CUDA 12.9 users should use `uv` with `--torch-backend=cu129`.
CUDA 13.0 and 12.9 wheels use a `manylinux_2_28` base. A non-root
`vllm-openai` image target and optional Python-only installation were added.

### Current build changes (`0.23-0.26`)

ROCm moved to PyTorch 2.11, XPU to torch-xpu 2.12, CUDA containers to GCC 12,
and `mistral_common` became optional. Require Starlette 1.0.1 or newer for its
security fix. The Transformers integration moved to 5.13.0.

### New runtime baseline (`0.27.1`)

The runtime uses PyTorch 2.13.0, torchvision 0.28.0, and Triton 3.7.1; CPU and
XPU builds also use torch 2.13. Rebuild containers and extensions for this
environment change.

## CLI, logging, metrics, and process controls

### CLI and observability migration (`0.7-0.10`)

Use the consolidated `vllm bench`; `--dataset` in `benchmark_serving.py` was
deprecated. `--help=page` gives paged help, and the CLI default model changed
to Qwen3-0.6B. The metrics
`vllm:time_in_queue_requests`,
`vllm:model_forward_time_milliseconds`, and
`vllm:model_execute_time_milliseconds` were deprecated;
`--show-hidden-metrics-for-version` temporarily exposes hidden metrics.
`vllm:cache_config_info`, KV-event publishing, and in-memory Prometheus access
were added, while misleading `gpu_` prefixes on non-GPU-specific metrics were
deprecated.

### Operational endpoints and TLS (`0.7-0.10`)

Use `/load` for load statistics and `/is_sleeping` for sleep state. The HTTP
server supports SSL key rotation, and `get_tokenizer_info` reports tokenizer
and chat-template information.

### Health and state reporting (`0.11-0.14`)

The health endpoint returns HTTP 503 when the engine is dead.
`/reset_prefix_cache` handles KV connectors and `/server_info` reports
environment information.

### Serving operations (`0.15-0.18`)

The server can derive `api_server_count` from data-parallel size. It supports
`--ssl-ciphers`, nested YAML configuration,
`--disable-access-log-for-endpoints`, multimodal and encoder cache clearing,
`--distributed-timeout-seconds`, and a graceful-shutdown timeout for in-flight
requests.

### Environment and timeout controls (`0.19-0.22`)

`VLLM_MAX_N_SEQUENCES` enforces a sequence limit, `VLLM_MEDIA_CACHE` opts into
media-URL caching, and `VLLM_SKIP_MODEL_NAME_VALIDATION` bypasses model-name
validation. CPU distributed execution has `--cpu-distributed-timeout-seconds`.

### Request and engine logging (`engine-and-openai-server`)

`--enable-log-requests` logs request IDs, parameters, and LoRA requests at
INFO; at DEBUG it also logs prompt text or token IDs. Set the threshold with
`VLLM_LOGGING_LEVEL`. `--aggregate-engine-logging` reports aggregate rather
than per-engine data-parallel statistics. `--fail-on-environ-validation`
promotes environment-validation failures to errors.

### CLI integration (`0.27.1`)

`vllm-bench` is integrated into the `vllm` CLI.

## Security and constrained environments

### Cache isolation and serialization (`0.7-0.10`)

Prefix caches support salting; completions and Responses requests can carry
`cache_salt`. Reproducible hashing is available through SHA-256 plus CBOR.
`VLLM_ALLOW_INSECURE_SERIALIZATION` and the V1 pickle-fallback switch control
unsafe serialization. Keep insecure deserialization disabled unless the data
path is fully trusted.

### Security corrections (`0.11-0.14`)

The releases addressed GHSA-wr9h-g72x-mwhm and CVE-2025-62164, prevented token
leaks through crash logs, and loaded PyTorch weights with `weights_only=True`.
They also corrected invalid UTF-8 token handling, CPU RoPE under
`--enforce-eager`, tool-call streaming completion, CPU scheduling stalls after
encoder-cache leaks, tools-plus-`response_format` crashes, and Voxtral
transcription.

### Security-sensitive loading (`0.15-0.18`)

NemotronVL and KimiK25 honor `trust_remote_code`; RLHF weight-sync
deserialization is gated by the insecure-serialization setting.

### Strict request validation (`0.23-0.26`)

Requests reject out-of-vocabulary token IDs, non-positive parallel or
scheduling knobs, non-finite temperature or repetition penalties, degenerate
structured-output configuration, and per-request GPU video-backend selection.
Invalid image URLs return HTTP 422. Regex and derender workloads have resource
bounds.

### Container resource detection (`0.27.1`)

The runtime respects cgroup memory limits on every platform and fails fast
when `/dev/shm` is too small. Provision shared memory explicitly in constrained
containers.
