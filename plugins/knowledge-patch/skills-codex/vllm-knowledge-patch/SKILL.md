---
name: vllm-knowledge-patch
description: vLLM
version: 0.26.0
license: MIT
metadata:
  author: Nevaberry
---


# vLLM Knowledge Patch

Use this skill when implementing, upgrading, extending, serving, or operating
vLLM. Start with the quick references below, then open the topic file that
matches the work. Treat the installed package, its configuration, and observed
runtime behavior as authoritative when they differ from this guidance.

## Reference index

| Reference | Topics |
| --- | --- |
| [engine-and-runtime.md](references/engine-and-runtime.md) | V1 architecture, scheduling, compilation, attention, Model Runner V2, sampling, lifecycle, streaming input, and offloading |
| [serving-apis.md](references/serving-apis.md) | Compatible HTTP APIs, Responses, chat, embeddings, transcription, realtime, render, Rust and gRPC frontends, validation, and endpoint plugins |
| [distributed-and-caching.md](references/distributed-and-caching.md) | Tensor, pipeline, data, expert, and sequence parallelism; Ray and native clusters; KV connectors, disaggregation, and tiered caches |
| [quantization-and-hardware.md](references/quantization-and-hardware.md) | Quantized formats, hardware boundaries, custom quantization plugins, accelerator targets, and KV-cache quantization |
| [speculative-decoding.md](references/speculative-decoding.md) | Draft methods, MTP, n-gram and suffix decoding, heterogeneous vocabularies, acceptance, structured output, and drafter controls |
| [models-multimodal-and-lora.md](references/models-multimodal-and-lora.md) | Model and task coverage, multimodal processing, pooling, Transformers backend behavior, and LoRA paths |
| [operations-and-migrations.md](references/operations-and-migrations.md) | Breaking removals, dependency transitions, CLI and metrics migrations, security fixes, containers, logging, and operational controls |

## Breaking changes first

### Use V1 interfaces only

V1 is the sole engine. Do not build new integrations on `AsyncLLMEngine`,
`LLMEngine`, `MQLLMEngine`, V0 attention backends, V0 executors, or the old V0
configuration surface. Custom model forward methods obtain KV cache and
attention metadata through `forward_context`, not explicit `kv_cache` and
`attn_metadata` parameters.

### Audit removed and renamed options during upgrades

Do not carry forward removed `num_lookahead_slots`, `best_of`, LoRA extra
vocabulary, `swap_space`, per-request logits processors, or the tokenizer
setter. Replace `--convert reward` with `--convert embed`; use
`--moe-backend` and `--linear-backend` instead of backend environment
variables. Use `device_ids` for placement because the runtime no longer sets
`CUDA_VISIBLE_DEVICES` internally.

### Pin request behavior explicitly

A model's `generation_config` can supply chat-template and sampling defaults.
Set temperature, token limits, seed, and related sampling controls explicitly
when stable behavior matters. `generation_config.max_tokens` is only a default,
not a hard ceiling; an explicit request may exceed it. `top_k=0` disables
top-k sampling.

### Revisit async scheduling and connector failure policy

Async scheduling evolved from experimental and unsafe in some preemption paths
to the normal path, and later gained pipeline-parallel and speculative-decoding
combinations. Validate it against the installed release and opt out where
needed. KV connector load failures default to failing the request; configure
recomputation explicitly if that is the intended recovery policy.

### Rebuild environments across dependency jumps

Wheel CUDA targets, PyTorch, Transformers, compilers, and container bases have
changed repeatedly. Rebuild images and native extensions rather than reusing
an older environment. Ray is no longer a default dependency, Python-only
installation is optional, and newer builds require a C++20-compatible compiler.

## Engine and configuration quick reference

### Understand the V1 execution model

`EngineCore` isolates scheduling and model execution. Tokenization, multimodal
preprocessing, detokenization, and response streaming overlap outside it.
Scheduling allocates token counts per request rather than treating prefill and
decode as separate phases. Prefix caching is cheap and normally enabled for
supported non-hybrid models; hybrid models keep it opt-in.

### Configure nested dataclasses safely

Pass a complete JSON object or use dotted flags such as:

```bash
vllm serve MODEL --attention-config.flash_attn_version=2
```

Nested JSON accepts decimal lowercase `k/m/g/t` and binary uppercase
`K/M/G/T` size suffixes. Do not set the same speculative field through both a
component shorthand and `--speculative-config`.

### Let automatic sizing work unless capacity is known

`--max-model-len auto` finds a context length that fits memory. Default batch
limits depend on hardware, offline versus server use, and performance mode;
they are also adjusted for context length and multimodal media. Inspect startup
KV-capacity and maximum-concurrency logs before overriding limits.

### Treat hybrid cache settings as correctness-sensitive

Chunked prefill follows model support. Disabling it on a supported generation
model or enabling it on an unsupported pooling model can crash or corrupt
output. Mamba and hybrid models use aligned prefix state with:

```bash
vllm serve MODEL --enable-prefix-caching --mamba-cache-mode align
```

### Choose attention and compilation deliberately

Use `--attention-backend` or `AttentionConfig`, not the retired attention
backend environment variable. `-O0` through `-O3` trade startup cost for
runtime performance; selective compilation uses `compile_ranges`. Hardware
defaults can change, including Blackwell MLA/prefill choices and cascade
attention, so pin a backend when reproducibility matters.

## Serving quick reference

### Know compatible-API omissions

Completions `suffix` and Chat `image_url.detail` are unsupported. Chat `user`
is accepted but ignored. `parallel_tool_calls=false` guarantees no more than
one call; the default permits multiple calls but does not guarantee them.

### Use the Responses lifecycle routes

Create at `/v1/responses`, retrieve at `/v1/responses/{response_id}`, and
cancel at `/v1/responses/{response_id}/cancel`. The API supports multi-turn
input, reasoning items, tools, structured output, streaming, and request-level
cache controls; verify the parser required by the selected model.

### Separate preprocessing when useful

Render endpoints and `vllm launch render` allow prompt preprocessing on a
GPU-less service. Engines can also consume async generators of `StreamingInput`
for session-oriented workloads such as speech recognition.

### Treat gRPC as private transport

The binary HTTP/2 server and Rust control plane provide health, abort, model,
server, and KV-event discovery. Even when TLS or mTLS is available on a
frontend, keep interfaces documented as private-use behind trusted network
boundaries.

## Distributed and cache quick reference

### Match parallelism to topology

Use pipeline parallelism with tensor parallel size one for uneven GPU counts or
poorly connected GPUs such as hosts without NVLink:

```bash
vllm serve MODEL --tensor-parallel-size 1 --pipeline-parallel-size 4
```

Native multi-node launch requires the multiprocessing data-parallel backend;
the node count must evenly divide `DP × PP × TP`. External data-parallel
balancing is MoE-only, requires a rank, and is required for fault tolerance.

### Secure Ray and provision shared memory

Ray cluster traffic is unencrypted and can carry unsafe payloads; bind each
container to a private per-node `VLLM_HOST_IP`. For GPUDirect RDMA, provide
locked memory and a memory-backed `/dev/shm`, then use `NCCL_DEBUG=TRACE` to
confirm `NET/IB/GDRDMA` rather than socket transport.

### Choose connector recovery and tiers explicitly

KV paths span CPU LRU offload, LMCache, NIXL, Mooncake, 3FS, FlexKV,
object-store and filesystem tiers, hybrid allocators, encoder caches, and
peer-to-peer secondary tiers. Check layout compatibility, block sizes,
prefill/decode parallelism, per-request policy, and failure behavior together.

## Quantization quick reference

### Validate method, checkpoint, and accelerator as a unit

Quantization names do not imply universal support. Check GPU generation,
CPU/XPU/ROCm/TPU path, linear versus MoE layers, checkpoint encoding, attention
backend, KV-cache dtype, and LoRA compatibility. TurboQuant KV cache currently
forces FlashAttention 2 when no compatible version is pinned.

### Register out-of-tree methods before selection

Decorate a `QuantizationConfig` subclass with
`@register_quantization_config("name")`, implement its dtype/capability/file
and dispatch contracts, import the registration module, then select the name.
Return a linear quantization method for `LinearBase` and a
`FusedMoEMethodBase` implementation for `FusedMoE`; the two contracts differ.

## Speculative decoding quick reference

### Use method-specific configuration

Use `method="suffix"` for draft-free dynamic-depth speculation,
`method="ngram"` for prompt lookup, `method="mtp"` for compatible assistant
checkpoints, and `method="draft_model"` for an explicit drafter. Custom
proposers use `method="custom_class"` with their fully qualified class in the
`model` field.

### Keep drafter and target settings separate

Use `draft_tensor_parallel_size` and the speculative configuration's
`max_model_len` for the drafter. `temperature` and `top_p` remain sampling
parameters. Heterogeneous vocabulary support is draft-model-only and greedy;
it intersects normalized token strings and limits proposals to shared tokens.

### Do not promise identical log probabilities

Rejection sampling preserves the target distribution up to numerical
precision, and greedy decoding is checked against non-speculative execution.
Token log probabilities can still vary with hardware precision and batch
composition.

## Working method

1. Inspect the installed vLLM version, model configuration, accelerator, and
   launch mode.
2. Open the relevant topic reference and identify defaults, removals, and
   feature constraints that affect that exact setup.
3. Prefer explicit request and engine settings when an upgrade changed a
   default.
4. Validate startup logs, health, cache capacity, request validation, and one
   representative generation path before production rollout.
5. For distributed changes, also validate rank arithmetic, network privacy,
   shared memory, connector failure handling, and graceful shutdown.
