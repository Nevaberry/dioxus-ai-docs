---
name: pytorch-knowledge-patch
description: PyTorch
license: MIT
version: "2.11.0"
metadata:
  author: Nevaberry
---

# PyTorch Knowledge Patch

Baseline: PyTorch through 2.3; covers 2.4.0–2.11.0 plus the compile-and-flexattention, fsdp2-and-float8, export-and-custom-ops, and serialization-security topic updates captured July 12, 2026.

## Use this skill

Read the reference file that matches the work before changing code. Start with
migrations and security when upgrading an existing project, then load the
specialized compiler, export, distributed, or platform reference as needed.
Treat APIs explicitly labeled API-unstable or experimental as subject to change.

## Reference index

| Reference | Topics |
| --- | --- |
| [migrations-and-security.md](references/migrations-and-security.md) | Safe checkpoint loading, repository trust, TorchScript, export/ONNX/PT2E removals, MAGMA and `varlen_attn` migrations |
| [compiler-and-attention.md](references/compiler-and-attention.md) | `torch.compile`, Dynamo, Inductor, FlexAttention, variable-length attention, cache, determinism, compiler debugging |
| [export-aot-and-custom-ops.md](references/export-aot-and-custom-ops.md) | `torch.export`, dynamic shapes, control flow, Core ATen, ONNX, AOTInductor packaging, Triton and out variants |
| [distributed-and-checkpointing.md](references/distributed-and-checkpointing.md) | FSDP2, DTensor, DCP, XCCL, context parallelism, functional collectives, Symmetric Memory, float8 |
| [platforms-extensions-and-runtime.md](references/platforms-extensions-and-runtime.md) | Wheels and ABI, CUDA/ROCm/XPU/MPS, C++/SYCL extensions, quantization, streams, autograd, profiler |

Coverage batches: `2.4.0`, `2.5.0`, `2.6.0`, `2.7.0`, `2.8.0`,
`2.9.0`, `2.10.0`, `2.11.0`, `compile-and-flexattention`,
`fsdp2-and-float8`, `export-and-custom-ops`, and `serialization-security`.

## Breaking changes and migrations

### Load checkpoints safely

Since 2.6, `torch.load()` defaults to `weights_only=True`. A plain tensor
`state_dict` normally needs no change. For other trusted objects, prefer an
explicit allowlist:

```python
state_dict = torch.load("weights.pt")

with torch.serialization.safe_globals([MyTensor]):
    value = torch.load("subclass.pt")
```

Use `weights_only=False` only for a trusted legacy pickle because loading can
execute arbitrary code. Use TorchFix to locate calls that rely on the implicit
default.

### Replace deprecated frontend and quantization APIs

- TorchScript is deprecated as of 2.10. Prefer `torch.export` for new export
  workflows.
- `torch.export.export_for_training()` is removed in 2.11. Use
  `torch.export.export()`; it now returns the equivalent graph.
- Core `torch.ao.quantization.pt2e` and `.quantizer` packages are removed in
  2.11. Install TorchAO and import from `torchao.quantization.pt2e`.
- The ONNX `fallback` argument is removed. Catch a failed dynamo export and
  invoke the legacy path explicitly when it is still required.

```python
from torchao.quantization.pt2e import prepare_pt2e, convert_pt2e
from torchao.quantization.pt2e.quantizer.x86_inductor_quantizer import (
    X86InductorQuantizer,
)
```

### Update `varlen_attn` calls for 2.11

All optional arguments are keyword-only. Replace `is_causal` with
`window_size`: `(-1, -1)` means full attention, `(-1, 0)` causal attention,
and `(W, 0)` a causal sliding window of size `W`.

```python
output = varlen_attn(
    query, key, value, cu_seq_q, cu_seq_k, max_q, max_k,
    window_size=(-1, 0), scale=1.0,
)
```

### Audit distributed construction and gradients

- Initialize process groups before constructing `DeviceMesh`; the mesh now
  snapshots its process-group registry for compiled `get_group()` tracing.
- If `DTensor.to_local()` sees a forward `Partial` placement and
  `grad_placements` is omitted, backward now maps it to `Replicate`. Pass the
  intended placements explicitly when another gradient layout is required.
- Remove calls to
  `torch.distributed.symmetric_memory.enable_symm_mem_for_group()`; the store
  now comes from the process group.

### Select compatible binaries

On Linux x86_64 and aarch64, the PyPI default in 2.11 is CUDA 13.0. CUDA 13
needs Turing (SM 7.5) or newer on Linux x86_64; CUDA 12.8 and 12.9 binaries also
drop Volta. Choose CUDA 12.6 for Maxwell, Pascal, or Volta, and choose an
explicit build on machines whose drivers support only CUDA 12.x.

```sh
pip install torch --index-url https://download.pytorch.org/whl/cu126
```

Manylinux 2.28 CUDA 12.6.3, AArch64, ROCm 6.2.4, and XPU builds introduced in
2.6 use `CXX11_ABI=1`; rebuild C++ and CUDA extensions with the same ABI.

## High-value compiler and attention updates

### Control compile behavior

Use compiler stances to choose behavior across invocations:

```python
torch.compiler.set_stance("eager_on_recompile")
```

This stance reuses compiled cache entries but falls back to eager execution
instead of recompiling. Use a region-scoped graph-break error when only part of
a compiled function must remain break-free:

```python
@torch.compile
def f(x):
    with torch._dynamo.error_on_graph_break():
        return x.sin()
```

For repeatable execution, call `torch.use_deterministic_algorithms(True)`
before compilation. To audit specialization, set
`torch._dynamo.config.error_on_recompile = True`.

### Save portable compiler caches

After compiling and running a workload, use
`torch.compiler.save_cache_artifacts()` and
`torch.compiler.load_cache_artifacts()` to move the complete cache to another
process or machine. Keep compilation inputs and decisions consistent across
distributed ranks; rank-specific recompilation can desynchronize collectives.

### Express FlexAttention sparsity efficiently

Use `score_mod` for fused score transforms and `BlockMask` for sparse patterns
that should skip whole blocks. Recompute a mask when captured data changes its
sparsity pattern, but reuse an invariant or per-batch mask across layers.

```python
from torch.nn.attention.flex_attention import create_block_mask, flex_attention

def causal(b, h, q_idx, kv_idx):
    return q_idx >= kv_idx

mask = create_block_mask(
    causal, B=None, H=None, Q_LEN=query.size(-2), KV_LEN=key.size(-2),
    _compile=True,
)
output = flex_attention(query, key, value, block_mask=mask)
```

Do not wrap `create_block_mask()` directly in `torch.compile()`; use its
`_compile=True` option. Returning `-inf` from `score_mod` is semantically valid
for masking but cannot skip masked blocks.

## High-value FSDP2 updates

FSDP1 is deprecated. Apply FSDP2 `fully_shard()` in place, bottom-up, and build
the optimizer afterward because parameters become sharded `DTensor`s:

```python
from torch.distributed.fsdp import fully_shard

model = Transformer()
for layer in model.layers:
    fully_shard(layer)
fully_shard(model)
optimizer = torch.optim.Adam(model.parameters(), lr=1e-2)
```

For meta-device construction, shard before storage materialization, then use
`to_empty()` and the module's reset method. Use `MixedPrecisionPolicy` at
module boundaries; BF16 gathered parameters can coexist with persistent FP32
shards, FP32 optimizer state, and FP32 reductions. Use DCP state-dict helpers
for full-state broadcast, gather, and CPU offload.

## High-value export updates

Choose dynamic-shape markers intentionally:

- `Dim.AUTO` may infer either dynamic behavior or specialization.
- `Dim.DYNAMIC` requires dynamism and fails if tracing specializes it.
- `Dim.STATIC` explicitly specializes the dimension.
- Sample dimensions of 0 or 1 specialize even under `AUTO`; use a sample
  greater than 1 when the dimension must vary.

Use named `Dim` values for equality, range, and linear relations. Avoid
concretizing symbolic values through `int()` or `range()`. Use tensor operators
or `torch._check()` to add runtime assertions and symbolic constraints.

Non-strict export executes ordinary Python and can freeze non-tensor results as
constants. Always inspect the resulting graph. Represent data-dependent
branches with `torch.cond`, keeping branch signatures and returned tensor
metadata identical and avoiding mutations.

## Stability notes

APIs described as API-unstable include the limited stable C++ ABI registration
surface, Symmetric Memory, XPUGraph, some compiler control-flow operators,
`DebugMode`, `varlen_attn`, FlashAttention-4-backed FlexAttention, and internal
AOTInductor packaging helpers. Pin and test against the exact PyTorch build when
using them.
