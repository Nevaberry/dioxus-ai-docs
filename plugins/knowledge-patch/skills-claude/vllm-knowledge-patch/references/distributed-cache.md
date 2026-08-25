# Distributed Execution, Parallelism, and Cache Topology

## Choosing and launching a topology

### Offline and asynchronous execution

Offline inference gained `torchrun` and SPMD-style execution in `0.7-0.10`,
and `AsyncLLM` gained a Ray executor. `LLM` became compatible with a
`torchrun` launcher; later in the same batch, multiprocess and `torchrun`
pipeline parallelism arrived, along with sequence parallelism combined with
pipeline parallelism.

### Pipeline parallelism for uneven or weakly connected GPUs

When a model fits on one node but its GPU count does not divide the model
cleanly, use pipeline parallelism with `tensor_parallel_size=1` and
`pipeline_parallel_size` equal to the GPU count. Prefer pipeline parallelism
over tensor parallelism on GPUs without NVLink, such as L40S, because it avoids
the latter's heavier communication.

```bash
vllm serve MODEL --tensor-parallel-size 1 --pipeline-parallel-size 4
```

### Native multi-node multiprocessing

`--nnodes/-n` requires the multiprocessing data-parallel backend. Node count
must evenly divide the `DP × PP × TP` world size, and `--node-rank/-r` is
zero-based. The engine derives local data-parallel size and rank and may use
the inferred rank for external load balancing.

Rank 0 runs the normal server; each worker connects to the same head address
with `--headless`:

```bash
vllm serve /path/to/model \
  --tensor-parallel-size 8 --pipeline-parallel-size 2 \
  --nnodes 2 --node-rank 1 \
  --master-addr HEAD_NODE_IP --headless
```

### External data-parallel balancing

External DP is rejected for non-MoE models, requires a rank, and forces local
DP size to one. The rank can be passed directly or inferred from a multi-node
launch. `--data-parallel-multi-port-external-lb` instead runs a node-local
supervisor with one API server per local rank and aggregated health.

`--enable-fault-tolerance` is rejected unless external balancing or an
explicit DP rank is active; internal balancing is unsupported. Constructing
`EngineArgs` with a dictionary-valued `fault_tolerance_config` enables fault
tolerance automatically.

### DP supervisor and selected-rank routing

Batch `0.19-0.22` added a data-parallel supervisor and forwarding of the
selected rank in `X-data-parallel-rank`. Batch `0.23-0.26` added node-targeted
Ray placement groups, per-GPU-worker RDMA NIC selection, a 120-second
coordinator startup timeout, and TLS for the DP supervisor.

## Ray cluster safety and diagnostics

Install the Ray executor with:

```bash
pip install "ray[cgraph]"
```

With `examples/ray_serving/run_cluster.sh`, assign every head or worker
container its own `VLLM_HOST_IP`, keep each launching shell open, and verify
membership with `ray status` and `ray list nodes`. Use private addresses that
untrusted hosts cannot reach: cluster traffic is unencrypted and its payload
format can permit arbitrary code execution.

Ray stopped being a default dependency in `0.15-0.18`, so deployments using
it must install it explicitly. RayExecutorV2 later became a default executor
path in `0.19-0.22`; dependency installation and executor selection remain
separate concerns.

## Capacity and transport diagnostics

### Read startup capacity estimates

`GPU KV cache size` is total token capacity in the GPU KV cache.
`Maximum concurrency for N tokens per request` estimates simultaneous
requests at `ModelConfig.max_model_len`. Add GPUs or nodes when these values
fall below the deployment's target, while remembering that request shape and
cache reuse still affect real concurrency.

### Configure GPUDirect RDMA prerequisites

Docker deployments should provide host IPC and `/dev/shm`. Kubernetes pods
should add `IPC_LOCK` and mount a memory-backed `emptyDir` at `/dev/shm`.

```bash
docker run --gpus all --ipc=host --shm-size=16G \
  -v /dev/shm:/dev/shm vllm/vllm-openai
```

Run with `NCCL_DEBUG=TRACE`. `[send] via NET/IB/GDRDMA` confirms GPUDirect
RDMA, whereas `[send] via NET/Socket` indicates inefficient TCP transport.

## Data and expert parallelism

Batch `0.7-0.10` added `--enable-expert-parallel` for DeepSeek, EP/TP MoE with
data-parallel attention, and data-parallel communication. It later added
elastic expert parallelism for changing GPU counts while preserving state and
exposed `MOE_DP_CHUNK_SIZE`.

Elastic expert parallelism became dynamically scalable for serving in
`0.15-0.18`; NIXL-EP integration and `--enable-ep-weight-filter` then allowed
loading to skip irrelevant expert weights.

Async EPLB became the default in `0.23-0.26`. NCCL-based EPLB combined with
async EPLB is rejected, and DeepEP v2 is available. Sequence parallelism can
run without data parallelism; hybrid-attention DCP and NIXL pipeline-parallel
prefill in push mode were added later in the batch.

## Disaggregated prefill and KV transfer

### Connector evolution

The LMCache connector in `0.7-0.10` supports KV-cache offload, disaggregated
prefill, and chunked prefill. NIXL integration and multiple KV connectors
followed.

Batch `0.11-0.14` added preparatory Prefill Context Parallelism and
cross-layer KV blocks, then the Mooncake Transfer Engine and external-launcher
mode. XBO, asymmetric-TP and heterogeneous-layout NIXL, cross-layer
MultiConnector layouts, and LMCache KV-cache registration followed.

Batch `0.19-0.22` added a 3FS KV connector and heterogeneous-TP
prefill/decode for Mamba2-like models, then bidirectional transfers between
prefill and decode.

Batch `0.23-0.26` enabled HMA by default for capable connectors. NIXL's
`kv_both` role began deprecation; `P2pNcclConnector` was removed. The same
batch added NIXL pipeline-parallel prefill in push mode.

In `0.27.1`, NIXL prefill/decode supports hybrid MLA+SSM models and
heterogeneous block sizes across the two sides. MoRIIO can route reads between
heterogeneous tensor-parallel prefill and data-parallel decode layouts.

## KV-cache offloading and tiering

### CPU offloading and selective weight movement

V1 added CPU KV-cache offloading with LRU management in `0.11-0.14`. Weight
Offloading V2 later gained prefetch, selective CPU offload, and pinned copies
that avoid doubling CPU memory (`0.15-0.18`).

KV-cache offloading in `0.15-0.18` can restrict CPU stores to frequently
reused blocks, use FlexKV as a backend, and describe multiple KV groups in one
offloading specification.

### Load-failure policy

From `0.15-0.18`, the KV-connector load-failure default changed from
`recompute` to `fail`. Configure transparent recomputation explicitly when
that behavior is required; otherwise a failed load fails the request.

### Policy and secondary tiers

Batch `0.19-0.22` added a pluggable CPU-offload `CachePolicy`, hybrid-model
support, Hybrid Memory Allocator integration, and `MooncakeStoreConnector`.
It then added multi-tier offloading beyond CPU memory: a Python filesystem
secondary tier, Mooncake disk offloading, and `reset_cache`.

Batch `0.23-0.26` added an object-store secondary tier, per-request policy via
`on_new_request`, async batched lookup, a parallelism-independent filesystem
tier, workload identity for object storage, `blocks_per_chunk` for
heterogeneous KV groups, and encoder-cache connectors with CPU offloading.

In `0.27.1`, tiering gained a generic peer-to-peer secondary tier with peer
lookup and serving. `TierFilter` and `TierMatcher` select tiers per request,
`TieringOffloadingSpec` makes KV events self-describing, and
`CachePolicyFactory` provides pluggable eviction policies.

## Cache reuse inside V1

V1 uses hash-based prefix lookup with LRU eviction, but constant-time eviction
and minimized allocation overhead make prefix caching inexpensive enough to
enable by default for supported non-hybrid models.

Multimodal requests have three distinct reuse paths: preprocessed inputs
shared across requests, image hashes participating in prefix-cache lookup, and
an encoder cache retaining vision embeddings. The encoder cache allows the
scheduler to split accompanying text prefill across steps rather than coupling
the image and all text into one operation.

Hybrid models keep prefix caching opt-in. Chunked prefill follows the model's
support declaration; forcing the wrong setting can crash or corrupt output.
RISC-V forces chunked prefill and prefix caching off.

## RLHF and weight-update distribution

Batch `0.15-0.18` added native NCCL weight synchronization, layerwise
reloading, pause/resume that preserves requests, an IPC weight-sync path, and
sleep level 0 with an enqueue/wait pattern.

Batch `0.19-0.22` added `/start_weight_update` and `/finish_weight_update` for
RLHF integrations. In `0.27.1`, rollout paths can tag weights with a version,
and the FlashInfer monolithic MoE kernel can return router-replay output for
training integrations.

## Failure checklist

- Validate `DP × PP × TP`, node count, zero-based rank, and head address before
  investigating worker code.
- Check whether external balancing is legal for the model and whether fault
  tolerance was enabled by configuration construction.
- Keep Ray membership and network reachability separate from NCCL transport
  and RDMA configuration.
- Confirm connector role, transfer direction, block layout, KV groups, and
  load-failure policy on both prefill and decode sides.
- For offload misses, identify the active policy, tier, object identity,
  request selector, and whether cache reset occurred.
