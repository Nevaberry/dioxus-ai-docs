# Distributed Training and Checkpointing

## Contents

- [Compose FSDP2 bottom-up](#compose-fsdp2-bottom-up)
- [Initialize meta-device modules](#initialize-meta-device-modules)
- [Control prefetching](#control-prefetching)
- [Apply mixed precision](#apply-mixed-precision)
- [Migrate FSDP1 configuration](#migrate-fsdp1-configuration)
- [Save and load distributed state](#save-and-load-distributed-state)
- [Use DeviceMesh and DTensor safely](#use-devicemesh-and-dtensor-safely)
- [Use differentiable collectives](#use-differentiable-collectives)
- [Select XCCL for Intel GPUs](#select-xccl-for-intel-gpus)
- [Use context parallelism](#use-context-parallelism)
- [Use Symmetric Memory](#use-symmetric-memory)
- [Combine FSDP2 with float8](#combine-fsdp2-with-float8)
- [Debug distributed jobs](#debug-distributed-jobs)

## Compose FSDP2 bottom-up

FSDP1 is deprecated in favor of FSDP2's in-place `fully_shard()`. Apply
sharding bottom-up to repeated child modules and then the root. Parameters of
already sharded children are excluded from the root parameter group. Modules
keep their original Python types while gaining `FSDPModule` methods.

Parameters become `DTensor`s with `Shard(0)` placement by default. Construct
the optimizer after sharding. Standard optimizers and
`torch.nn.utils.clip_grad_norm_()` operate directly on these parameters.

```python
from torch.distributed.fsdp import fully_shard

model = Transformer()
for layer in model.layers:
    fully_shard(layer)
fully_shard(model)

optimizer = torch.optim.Adam(model.parameters(), lr=1e-2)
```

## Initialize meta-device modules

For construction on the meta device, apply `fully_shard()` before allocating
storage. Materialize with `to_empty()` and then call the module's normal reset
method. This replaces FSDP1's `param_init_fn` path.

```python
with torch.device("meta"):
    model = Transformer()

for layer in model.layers:
    fully_shard(layer)
fully_shard(model)
model.to_empty(device="cuda")
model.reset_parameters()
```

## Control prefetching

FSDP2 implicitly prefetches one next all-gather at a time and reverses the
post-forward order during backward. CPU-bound workloads, or workloads that can
spend additional memory on multiple prefetched layers, can set explicit
forward and backward schedules:

```python
for i in range(len(model.layers) - 1):
    model.layers[i].set_modules_to_forward_prefetch([model.layers[i + 1]])

for i in range(1, len(model.layers)):
    model.layers[i].set_modules_to_backward_prefetch([model.layers[i - 1]])
```

Calling `model.unshard()` before `model(x)` launches the first all-gather early
enough to overlap preceding work:

```python
model.unshard()
loss = model(x).sum()
```

## Apply mixed precision

`MixedPrecisionPolicy` casts gathered parameters at each module's
forward/backward boundary and can use a separate reduction dtype. With BF16
compute and FP32 reductions, persistent parameter shards and optimizer state
remain FP32, while only gathered compute parameters are BF16. Policies can
differ by layer.

```python
from torch.distributed.fsdp import MixedPrecisionPolicy

policy = MixedPrecisionPolicy(
    param_dtype=torch.bfloat16,
    reduce_dtype=torch.float32,
)
for layer in model.layers:
    fully_shard(layer, mp_policy=policy)
fully_shard(model, mp_policy=policy)
```

## Migrate FSDP1 configuration

Translate FSDP1 sharding strategies as follows:

- `FULL_SHARD` becomes `reshard_after_forward=True`.
- `SHARD_GRAD_OP` becomes `reshard_after_forward=False`.
- Hybrid variants use the corresponding Boolean with a 2D device mesh.
- Parameter CPU offload becomes `CPUOffloadPolicy()`.
- Backward prefetch is always `BACKWARD_PRE`; `BACKWARD_POST` is unsupported.
- `device_id` is inferred from the device mesh.

Buffers are not sharded, so `buffer_dtype` is gone. `output_dtype` is new.
`cast_forward_inputs` replaces both root and non-root input-casting controls.

State synchronization moves to Distributed Checkpoint with
`broadcast_from_rank0=True`. `limit_all_gathers` is unnecessary because FSDP2
avoids the associated CPU synchronization. Original parameters are always
retained rather than flattened. Replace `no_sync()` with
`set_requires_gradient_sync()`. FSDP1's `ignored_params` and `ignored_states`
inputs consolidate into FSDP2's `ignored_params`.

## Save and load distributed state

`model.state_dict()` returns sharded `DTensor` values. For custom conversion,
all-gather one with `full_tensor()`. Convert a full tensor back with
`distribute_tensor(full, sharded_meta.device_mesh, sharded_meta.placements)`
and load into a meta-initialized module with `assign=True`.

For a standard full-checkpoint path, Distributed Checkpoint can shard and
broadcast a rank-0 state dict during load, or all-gather and CPU-offload during
save:

```python
from torch.distributed.checkpoint.state_dict import (
    StateDictOptions,
    get_model_state_dict,
    set_model_state_dict,
)

set_model_state_dict(
    model=model,
    model_state_dict=full_state_dict,
    options=StateDictOptions(
        full_state_dict=True,
        broadcast_from_rank0=True,
    ),
)

full_state_dict = get_model_state_dict(
    model=model,
    options=StateDictOptions(full_state_dict=True, cpu_offload=True),
)
```

Since 2.8.0, Distributed Checkpoint can save, load, and re-shard checkpoints in
the Hugging Face SafeTensors format.

## Use DeviceMesh and DTensor safely

In 2.11.0, `DeviceMesh` snapshots its process-group registry when constructed
so `torch.compile` can trace `get_group()`. Initialize process groups before
creating the mesh. Groups added later may be absent during compiled lookup.

Also in 2.11.0, omitting `grad_placements` from `DTensor.to_local()` maps a
forward `Partial` placement to `Replicate` in backward rather than preserving
`Partial`. Pass an explicit layout when another gradient placement is needed:

```python
local_tensor = partial_dtensor.to_local(grad_placements=[Replicate()])
```

## Use differentiable collectives

API-unstable functional distributed collectives are differentiable as of
2.11.0, so autograd can backpropagate through them without a custom autograd
function. Non-functional collectives such as
`torch.distributed.all_gather()` also work automatically under
`FakeTensorMode`; their meta implementations are registered when PyTorch is
imported.

## Select XCCL for Intel GPUs

XCCL, added in 2.8.0, provides Intel XPU collectives for DDP, FSDP, pipeline
parallelism, and tensor parallelism. Backend selection may choose it
transparently for XPU, or name it explicitly:

```python
torch.distributed.init_process_group(backend="xccl")
```

## Use context parallelism

The prototype native Context Parallel API added in 2.7.0 supplies a Python
context in which every
`torch.nn.functional.scaled_dot_product_attention()` call uses context
parallelism. Supported attention implementations include Flash Attention,
Efficient Attention, and cuDNN Attention.

## Use Symmetric Memory

The API-unstable Symmetric Memory programming surface added in 2.9.0 allocates
tensors that remote GPUs can access directly through CUDA or NVSHMEM backends.
Operations live under `torch.ops.symm_mem`. The surface includes direct-access
collectives, MoE-oriented `all_to_all_vdev` variants, and an NVSHMEM plugin for
custom multi-GPU Triton kernels.

In 2.11.0 it adds NCCL 2.29 one-sided operations, a window API, NCCL memory-pool
support, and offset access. Remove
`torch.distributed.symmetric_memory.enable_symm_mem_for_group()`; it is
deprecated and unnecessary because the store is obtained directly from the
process group.

## Combine FSDP2 with float8

FSDP2's tensor-subclass extension point can customize weight all-gather. Uses
include float8 communication for float8 linears and NF4 communication for
QLoRA.

The demonstrated float8 training stack combines TorchAO float8 linear compute,
FSDP2 float8 weight all-gathers, tensor-wise scaling, and `torch.compile`.
Scaled dot-product attention remains BF16: enabling float8 linear compute and
communication does not move attention itself to float8.

## Debug distributed jobs

Since 2.11.0, `torch.distributed.debug.start_debug_server()` accepts
`start_method="fork"`, `"spawn"`, or `"forkserver"`; select a CUDA-safe
startup method. Distributed debugging can also emit periodic dumps. The C++
`DebugInfoWriter` writes beneath `$XDG_CACHE_HOME/torch` when
`XDG_CACHE_HOME` is set, falling back to `~/.cache/torch` otherwise.
