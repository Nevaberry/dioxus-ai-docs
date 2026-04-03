# Distributed Training (2.7–2.11)

## FSDP2: fully_shard (replaces FSDP1, deprecated in 2.8)

FSDP1 (`FullyShardedDataParallel` wrapper) is deprecated. Use FSDP2's `fully_shard` function.

```python
from torch.distributed.fsdp import fully_shard

model = Transformer()
for layer in model.layers:
    fully_shard(layer)  # Shard each layer
fully_shard(model)       # Shard root

# Parameters become DTensors, sharded on dim-0
# Optimizer constructed AFTER fully_shard
optim = torch.optim.Adam(model.parameters(), lr=1e-2)

# Training loop unchanged
loss = model(x).sum()
loss.backward()
optim.step()
```

## Context Parallel API (2.7)

Run SDPA with context parallelism across GPUs for long-sequence training.

```python
from torch.distributed.tensor.parallel import context_parallel

# Every SDPA call within this context runs with context parallelism
with context_parallel(mesh):
    output = torch.nn.functional.scaled_dot_product_attention(q, k, v)
```

## SafeTensors Support in Distributed Checkpointing (2.8)

DCP can now save/load in HuggingFace SafeTensors format.

```python
import torch.distributed.checkpoint as dcp
# Save in safetensors format
dcp.save(state_dict, storage_writer=dcp.FileSystemWriter(path, format="safetensors"))
```

## Symmetric Memory for Multi-GPU Kernels (2.9)

In-kernel GPU-to-GPU communication over NVLink/RDMA.

```python
# Accelerated collectives under torch.ops.symm_mem
# e.g. one_shot_all_reduce, all_to_all_vdev for MoE
# Backends: CUDA, NVSHMEM
```

## Differentiable Collectives (2.11)

Functional collectives now support backpropagation, enabling training workflows that differentiate through collective ops without custom autograd functions.
