---
name: vllm-knowledge-patch
description: vLLM
version: "0.26.0"
license: MIT
metadata:
  author: Nevaberry
---


# vLLM Knowledge Patch

Use this skill when changing, deploying, extending, or debugging vLLM. Start
with the quick references below, then load the topic file that matches the
work. Treat a project's manifests, runtime help, logs, and tests as the final
authority when behavior depends on the installed build or accelerator.

## Reference index

| Reference | Topics |
| --- | --- |
| [Engine, Runtime, and Configuration](references/engine-runtime.md) | V1 architecture, scheduling, compilation, batching, configuration, sampling, Model Runner V2, dependencies, and removals |
| [Serving APIs, Operations, and Security](references/serving-apis.md) | HTTP, Responses, Chat, embeddings, speech, parsers, Rust frontend, gRPC, metrics, logging, TLS, validation, and security |
| [Distributed Execution, Parallelism, and Cache Topology](references/distributed-cache.md) | TP/PP/DP/EP, Ray and multiprocessing, disaggregation, KV connectors, offloading, fault tolerance, and RDMA |
| [Models, Multimodal Integration, Adapters, and Lifecycle](references/models-adapters.md) | Model and task coverage, multimodal processing, loading, LoRA, pooling, lifecycle, and RL integrations |
| [Quantization Formats, Hardware, and Extensions](references/quantization-hardware.md) | Checkpoint formats, KV-cache quantization, hardware support, custom quantization plugins, wheels, and accelerators |
| [Speculative Decoding](references/speculative-decoding.md) | Methods, configuration, acceptance, heterogeneous vocabularies, structured output, and evolving execution combinations |

## Breaking changes and migration checks

### Assume V1-only interfaces

- Do not build new integrations around `AsyncLLMEngine`, `LLMEngine`,
  `MQLLMEngine`, V0 executors, or V0 attention backends. The remaining V0
  interfaces and backends were removed after V1 became the default.
- Custom model `forward` methods must obtain KV-cache and attention metadata
  through `forward_context`; the old `kv_cache` and `attn_metadata` arguments
  are gone.
- Recheck extensions that depended on legacy PagedAttention, old tokenizer or
  chat-template import locations, or legacy `api_server.py` placement.

### Audit removed and renamed settings

- Replace `VLLM_ATTENTION_BACKEND` with `--attention-backend` or
  `AttentionConfig`/`attention_config`.
- Replace `--convert reward` with `--convert embed`.
- Replace non-GPU-specific metric names carrying a `gpu_` prefix and migrate
  from removed `vllm:time_per_output_token_seconds` to
  `vllm:inter_token_latency_seconds`.
- Remove use of `num_lookahead_slots`, `best_of`, LoRA extra vocabulary,
  `swap_space`, per-request logits processors, `reasoning_content`,
  `VLLM_ALL2ALL_BACKEND`, BitBlas, Marlin 24, DeepSpeedFp8, and RTN where the
  deployed version no longer accepts them.
- Do not depend on vLLM mutating `CUDA_VISIBLE_DEVICES`; pass `device_ids` for
  explicit placement. Existing visibility masks change how integer device IDs
  are interpreted.

### Re-pin environment dependencies on upgrade

- Rebuild images and native extensions when the PyTorch, CUDA, Triton,
  Transformers, compiler, or manylinux baseline changes.
- Ray is no longer guaranteed as a default dependency; install the executor
  extras explicitly when using Ray.
- Treat cgroup memory and `/dev/shm` checks as startup requirements in
  constrained containers.

## Defaults that can change output or availability

### Make sampling explicit

- V1's seed default became deterministic. Set the seed deliberately when
  comparing runs, and do not assume caller RNG isolation when V1
  multiprocessing is disabled.
- Use `top_k=0` to disable top-k sampling; `-1` is only a compatibility
  sentinel on releases that still accept it.
- Set temperature and other sampling values explicitly when model
  `generation_config` defaults must not alter behavior after a model change.
- Treat `generation_config.max_tokens` as a request default, not necessarily a
  hard ceiling; explicit request values can override it on newer releases.
- Unsupported speculative-decoding sampling parameters can be rejected rather
  than ignored.

### Re-evaluate scheduler and cache defaults

- Async scheduling became default for many supported configurations after an
  earlier period with corruption hazards. Opt out with
  `--no-async-scheduling` when the deployed combination is unsupported.
- Pipeline parallelism is supported with async scheduling on newer releases,
  but other exclusions can remain hardware- and method-specific.
- V1 enables prefix caching cheaply for ordinary supported models, while
  hybrid models keep it opt-in and RISC-V forces it off with chunked prefill.
- KV-connector load failures default to failing the request on newer releases;
  configure recomputation explicitly if that is the intended policy.
- Cascade attention is no longer assumed enabled, and backend defaults differ
  across Blackwell, SM90+, sparse MLA, and KV-cache formats.

### Understand automatic sizing

- `--max-model-len auto` selects a context length that fits available GPU
  memory.
- Scheduler token and sequence defaults vary by device class, offline versus
  server use, and performance mode. Explicit limits take precedence.
- Automatic batched-token limits account for model context, multimodal media,
  sequence limits, and chunked-prefill support.
- Use startup `GPU KV cache size` and maximum-concurrency estimates as capacity
  signals, not promises independent of request shape.

## Configuration quick reference

### Prefer structured configuration

- Dataclass-backed CLI options accept a whole JSON object or dotted keys, such
  as `--attention-config.flash_attn_version=2`.
- Size values accept decimal `k/m/g/t` and binary `K/M/G/T` suffixes in the
  supported batch, scheduling, KV-memory, and prefetch settings.
- Nested YAML configuration is supported; use it for repeatable deployments
  instead of long unreviewable command lines.
- Speculation shorthands `--spec-method`, `--spec-model`, and `--spec-tokens`
  populate `--speculative-config`, but must not duplicate fields already set
  in the JSON object.

### Choose execution topology deliberately

- Prefer pipeline parallelism with `tensor_parallel_size=1` when GPU counts do
  not divide model layers cleanly or the GPUs lack fast interconnects such as
  NVLink.
- Native multi-node launch requires the multiprocessing DP backend and an
  `nnodes` count that evenly divides `DP × PP × TP`.
- External data-parallel balancing is MoE-only, forces local DP size to one,
  and requires an explicit or inferred rank.
- Fault tolerance requires external balancing or an explicit DP rank; it is
  not available with internal balancing.
- Keep Ray cluster traffic on private per-node addresses. Its transport is not
  an untrusted-network boundary.

## Serving quick reference

### OpenAI-style endpoints

- The request `model` field can be optional. Supported surfaces include
  Chat/Completions, Responses, `/score`, embeddings, reranking, transcription,
  batch chat, and extensible endpoints; exact availability is version- and
  frontend-dependent.
- Completions `suffix` and Chat `image_url.detail` are unsupported. Chat's
  `user` is accepted but ignored.
- `parallel_tool_calls=false` limits output to at most one tool call; `true`
  permits but cannot force multiple calls.
- Responses can be retrieved and cancelled by response ID. Newer surfaces add
  structured outputs, reasoning events, prompt embeddings, namespace tools,
  tool streaming, and chat-template parameters.
- Validate frontend parity before switching between Python and Rust; the Rust
  path has its own rollout of auth, CORS, pause/resume, TLS, multimodal, and
  benchmark support.

### Operations and observability

- A dead engine returns HTTP 503 from health checks. Use `/server_info`,
  `/load`, `/is_sleeping`, pause/resume, cache-reset, and tokenizer-info routes
  only where supported by the selected frontend.
- `--enable-log-requests` logs identifiers and parameters at INFO and prompt
  content at DEBUG. Choose `VLLM_LOGGING_LEVEL` with that disclosure boundary
  in mind.
- Use `--aggregate-engine-logging` for aggregate DP statistics and
  `--fail-on-environ-validation` to make validation failures fatal.
- Rotate TLS keys through the server facility where supported; configure
  cipher policy and graceful-shutdown timeouts explicitly.
- Treat the gRPC interface described as private-use as unsuitable for an
  exposed network even when a later frontend adds TLS or mTLS.

## Model, multimodal, and adapter quick reference

- V1 out-of-tree multimodal support uses the merged processor plus the
  appropriate `get_*_embeddings` methods. The legacy input mapper is not a
  future-proof extension point.
- Multimodal preprocessing, processor caches, prefix hashes, and encoder
  caches are distinct reuse layers; size and secure them independently.
- Model Runner V2 is selected automatically for increasing model families and
  can fall back when a requested feature is unsupported. Verify the runner in
  logs before attributing behavior to it.
- LoRA support spans sharded MoE, multimodal towers/connectors, remote
  resolvers, quantized adapters, audio adapters, and target-module filtering,
  but each path has model and backend constraints.
- Use `LLM.sleep`, `LLM.wake_up`, pause/resume, weight reload/update, and
  synchronization APIs according to the integration's request-preservation
  and serialization requirements.

## Quantization and speculation quick reference

- Check both the quantization format and accelerator generation. A format name
  alone does not establish kernel availability, KV-cache support, or LoRA
  compatibility.
- Per-layer `QuantSpec` configuration separates `linear` and `moe` choices;
  out-of-tree methods register a `QuantizationConfig` and return layer-specific
  method implementations.
- TurboQuant KV cache currently forces FlashAttention 2 when an incompatible
  version is selected implicitly.
- In speculative decoding, use `draft_tensor_parallel_size` inside
  `speculative_config`; target-model `tensor_parallel_size` is not a substitute.
- Heterogeneous-vocabulary speculation is draft-model-only and greedy-only.
  Token distribution can remain lossless while individual log probabilities
  still vary with precision and batching.
- Cloud-storage model URIs skip automatic speculator detection; configure the
  method and proposer explicitly.

## Debugging order

1. Confirm the installed vLLM build, frontend, runner, accelerator, wheel, and
   dependency versions.
2. Capture the resolved engine configuration and startup capacity logs.
3. Make sampling, scheduling, attention, cache, and topology settings explicit.
4. Reduce to one frontend and one execution topology before testing adapters,
   quantization, or speculative decoding.
5. For distributed failures, verify ranks, private addresses, `/dev/shm`,
   locked memory, Ray membership, and NCCL transport selection.
6. For output drift, compare generation configuration, seed, parser, chat
   template, tokenizer, speculative method, and logprob mode.
7. Load the matching reference file before changing a deprecated interface or
   assuming support for a model, hardware generation, or endpoint.
