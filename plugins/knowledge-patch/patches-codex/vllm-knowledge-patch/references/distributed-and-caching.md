# Distributed Execution and Caching

Use this reference for parallel execution, cluster launch, disaggregated
serving, KV transfer and offload, expert scaling, topology, and cache capacity.

## Parallel execution modes

### Offline launch and early parallel combinations (`0.7-0.10`)

Offline inference supports `torchrun` and SPMD-style execution. `AsyncLLM`
has a Ray executor and `LLM` works under a `torchrun` launcher. Multiprocess
and `torchrun` pipeline parallelism are supported, as is sequence parallelism
combined with pipeline parallelism.

Expert parallelism for DeepSeek models uses `--enable-expert-parallel`. EP/TP
MoE can run with data-parallel attention and data-parallel communication.
Elastic expert parallelism can change GPU counts while preserving state;
`MOE_DP_CHUNK_SIZE` controls MoE data-parallel chunking.

### New distributed layouts (`0.11-0.14`)

Preparatory Prefill Context Parallelism and cross-layer KV blocks were added,
followed by the Mooncake Transfer Engine and external-launcher mode. Later
layouts include XBO, asymmetric-TP and heterogeneous-layout NIXL, cross-layer
MultiConnector arrangements, and LMCache KV-cache registration.

### Dynamic expert serving (`0.15-0.18`)

Elastic expert parallelism supports dynamic GPU scaling. NIXL-EP integrates
with that path, and `--enable-ep-weight-filter` skips irrelevant expert weights
during load.

### Data-parallel supervisor and bidirectional transfer (`0.19-0.22`)

Disaggregated serving supports a 3FS KV connector, heterogeneous-TP
prefill/decode for Mamba2-like models, and bidirectional KV transfers. The
data-parallel supervisor forwards the selected rank in the
`X-data-parallel-rank` header.

### New defaults and hybrid layouts (`0.23-0.26`)

Async EPLB is the default. NCCL-based EPLB combined with async EPLB is
rejected; DeepEP v2 is available. Sequence parallelism can run without data
parallelism. Hybrid-attention DCP and NIXL pipeline-parallel prefill in push
mode are supported.

Ray placement groups can target nodes, each GPU worker can select an RDMA NIC,
the coordinator startup timeout is 120 seconds, and the data-parallel
supervisor supports TLS.

## Native multi-node and external balancing

### World-size arithmetic (`engine-and-openai-server`)

`--nnodes/-n` requires the multiprocessing data-parallel backend. Node count
must evenly divide `DP × PP × TP`, and `--node-rank/-r` is zero-based. The
engine derives local data-parallel size and rank and may use that rank for
external load balancing.

### External balancing and fault tolerance (`engine-and-openai-server`)

External data parallelism is MoE-only, requires a rank, and forces local
data-parallel size to one. Supply the rank directly or infer it from
multi-node launch. `--data-parallel-multi-port-external-lb` runs a node-local
supervisor with one API server per local rank and aggregate health.

`--enable-fault-tolerance` requires external balancing or an explicit
data-parallel rank; internal balancing is unsupported. Passing a dictionary as
`fault_tolerance_config` to `EngineArgs` enables fault tolerance automatically.

### Headless workers (`distributed-parallelism`)

For native multi-node multiprocessing, rank 0 runs the normal server and every
worker connects to its head address with `--headless`:

```bash
vllm serve /path/to/model \
  --tensor-parallel-size 8 --pipeline-parallel-size 2 \
  --nnodes 2 --node-rank 1 \
  --master-addr HEAD_NODE_IP --headless
```

## Topology and capacity

### Pipeline parallelism for uneven or weakly connected GPUs (`distributed-parallelism`)

If a model fits on one node but the GPU count does not divide it evenly, use
`tensor_parallel_size=1` and set `pipeline_parallel_size` to the GPU count.
Pipeline parallelism is also preferable on GPUs without NVLink, such as L40S,
because tensor parallelism has heavier communication:

```bash
vllm serve MODEL --tensor-parallel-size 1 --pipeline-parallel-size 4
```

### Read capacity from startup logs (`distributed-parallelism`)

`GPU KV cache size` is total GPU KV token capacity. `Maximum concurrency for N tokens per request`
estimates simultaneous requests at
`ModelConfig.max_model_len`. Add GPUs or nodes if either value misses the
deployment target.

### Device ID composition (`engine-and-openai-server`)

If a device-visibility environment variable already masks devices, integer
values in `--device-ids` index the visible list rather than raw physical
devices. UUIDs are accepted, but integer and UUID forms cannot be mixed;
duplicates are rejected. `--device-ids` has no effect with Ray executors.

## Ray cluster safety and RDMA

### Containerized Ray (`distributed-parallelism`)

Install the executor with:

```bash
pip install "ray[cgraph]"
```

With `examples/ray_serving/run_cluster.sh`, give every head and worker
container a distinct `VLLM_HOST_IP`, keep each launching shell open, and verify
membership with `ray status` and `ray list nodes`. Use private addresses that
untrusted hosts cannot reach: cluster traffic is unencrypted and its payload
format can allow arbitrary code execution.

### GPUDirect RDMA (`distributed-parallelism`)

Docker needs host IPC and `/dev/shm`; Kubernetes needs `IPC_LOCK` plus a
memory-backed `emptyDir` mounted at `/dev/shm`:

```bash
docker run --gpus all --ipc=host --shm-size=16G \
  -v /dev/shm:/dev/shm vllm/vllm-openai
```

Run with `NCCL_DEBUG=TRACE`. `[send] via NET/IB/GDRDMA` confirms GPUDirect
RDMA; `[send] via NET/Socket` indicates inefficient TCP transport.

## KV connectors and disaggregation

### LMCache, NIXL, and multiple connectors (`0.7-0.10`)

LMCache supports KV offload, disaggregated prefill, and chunked prefill. NIXL
integration and multiple simultaneous KV connectors were added later.

### Policy-aware and tiered offload (`0.19-0.22`)

CPU offload has a pluggable `CachePolicy` and supports hybrid models. It
integrates with the Hybrid Memory Allocator and `MooncakeStoreConnector`.
Multi-tier offload can extend beyond CPU memory to a Python filesystem tier or
Mooncake disk, and exposes `reset_cache`.

### Request and object-store controls (`0.23-0.26`)

An object-store secondary tier is available, and capable connectors enable HMA
by default. `on_new_request` selects per-request offload policy. The cache also
supports async batched lookup, a parallelism-independent filesystem tier,
workload identity for object storage, `blocks_per_chunk` for heterogeneous KV
groups, and encoder-cache connectors with CPU offload.

### Hybrid disaggregation (`0.27.1`)

NIXL prefill/decode disaggregation supports hybrid MLA+SSM models and different
block sizes between prefill and decode. MoRIIO routes reads between
heterogeneous tensor-parallel prefill and data-parallel decode layouts.

### Peer and policy extension points (`0.27.1`)

KV offload supports a generic peer-to-peer secondary tier with lookup and
serving. `TierFilter` and `TierMatcher` select tiers per request;
`TieringOffloadingSpec` makes KV events self-describing; and
`CachePolicyFactory` supplies pluggable eviction policies.
