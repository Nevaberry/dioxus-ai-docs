---
name: pytorch-knowledge-patch
description: PyTorch 2.6–2.11 changes — weights_only=True default, FSDP2 fully_shard, torch.compile improvements (mega cache, hierarchical compilation, control flow ops), varlen_attn, FlexAttention FA4, Dim.AUTO export, TorchScript deprecated. Load before writing PyTorch code.
license: MIT
version: "2.11.0"
metadata:
  author: Nevaberry
---

# PyTorch Knowledge Patch

Claude's baseline knowledge covers PyTorch through 2.5. This skill provides changes from PyTorch 2.6 through 2.11 (2025-01 to 2026-03).

## Quick Reference — Key API Changes

| Feature | API | Since |
|---------|-----|-------|
| Safe loading default | `torch.load()` now `weights_only=True` | 2.6 |
| Compile stance control | `torch.compiler.set_stance("eager_on_recompile")` | 2.6 |
| Custom Triton ops | `@torch.library.triton_op("lib::name", mutates_args=())` | 2.6 |
| Auto dynamic shapes | `Dim.AUTO` in `torch.export` | 2.6 |
| Mega cache (portable) | `torch.compiler.save_cache_artifacts()` / `load_cache_artifacts()` | 2.7 |
| Context parallelism | `context_parallel(mesh)` context manager for SDPA | 2.7 |
| Foreach map | `torch._foreach_map(fn, tensors, ...)` | 2.7 |
| Control flow ops | `cond`, `while_loop`, `scan`, `associative_scan` | 2.8 |
| Hierarchical compile | `torch.compiler.nested_compile_region()` | 2.8 |
| DCP SafeTensors | `dcp.FileSystemWriter(path, format="safetensors")` | 2.8 |
| FSDP1 deprecated | Use `fully_shard()` (FSDP2) instead | 2.8 |
| Symmetric memory | `torch.ops.symm_mem` for in-kernel collectives | 2.9 |
| Graph break errors | `torch._dynamo.error_on_graph_break()` | 2.9 |
| Variable-length attn | `varlen_attn(q, k, v, cu_seqlens_q, ...)` | 2.10 |
| TorchScript deprecated | Use `torch.export` instead | 2.10 |
| Deterministic compile | `torch.use_deterministic_algorithms(True)` applies to compile | 2.10 |
| DebugMode | `torch.debugging.DebugMode()` for numerical debugging | 2.10 |
| Differentiable collectives | Functional collectives support backprop | 2.11 |
| FlexAttention + FA4 | Auto FA4 kernels on Hopper/Blackwell | 2.11 |
| CUDA 13 default | CUDA 12.8 via `download.pytorch.org/whl/cu128` | 2.11 |

## BREAKING: torch.load defaults to weights_only=True (2.6)

`torch.load("file.pt")` now uses `weights_only=True` by default. Loading full `nn.Module` objects will fail.

```python
# Old code that breaks:
model = torch.load("model.pt")  # fails if saved with torch.save(model)

# Fix: load state_dict (recommended)
model.load_state_dict(torch.load("model.pt", weights_only=True))

# Fix: explicitly opt into unsafe loading
model = torch.load("model.pt", weights_only=False)
```

For tensor subclasses/numpy arrays, use `torch.serialization.safe_globals` to allowlist classes.

## FSDP2: fully_shard (replaces FSDP1)

FSDP1 (`FullyShardedDataParallel` wrapper) is deprecated since 2.8. Use FSDP2:

```python
from torch.distributed.fsdp import fully_shard

model = Transformer()
for layer in model.layers:
    fully_shard(layer)  # Shard each layer
fully_shard(model)       # Shard root

# Parameters become DTensors, sharded on dim-0
# Optimizer constructed AFTER fully_shard
optim = torch.optim.Adam(model.parameters(), lr=1e-2)
```

See `references/distributed-training.md` for context parallelism, symmetric memory, differentiable collectives, and SafeTensors DCP support.

## torch.compile Improvements

### Mega Cache — Portable Compilation Artifacts (2.7)

```python
artifacts = torch.compiler.save_cache_artifacts()
# Save to disk, transfer to another machine...
torch.compiler.load_cache_artifacts(artifacts)
```

### Hierarchical Compilation — Compile Once, Reuse (2.8)

```python
@torch.compile
def model_forward(x):
    for layer in layers:
        with torch.compiler.nested_compile_region():
            x = layer(x)  # Compiled once, reused for all layers
    return x
```

### Control Flow Without Graph Breaks (2.8)

Five operators: `cond`, `while_loop`, `scan`, `associative_scan`, `map`.

```python
from torch._higher_order_ops.cond import cond
from torch._higher_order_ops.scan import scan

result = cond(pred_tensor, true_fn, false_fn, operands)
carry, outputs = scan(combine_fn, init_carry, xs)
```

### error_on_graph_break() — Targeted Graph Break Errors (2.9)

```python
with torch._dynamo.error_on_graph_break():
    # Errors on graph breaks here (unlike fullgraph which is all-or-nothing)
    compiled_fn(x)
```

See `references/torch-compile.md` for set_stance and deterministic mode.

## torch.export & Custom Ops

### Dim.AUTO — Automatic Dynamic Shapes (2.6)

```python
from torch.export import export, Dim
ep = export(model, (x,), dynamic_shapes={"x": {0: Dim.AUTO}})
# Automatically infers min/max ranges, relations between dims, static/dynamic behavior
```

### torch.library.triton_op — Custom Triton Kernels (2.6)

```python
@torch.library.triton_op("mylib::add", mutates_args=())
def add(x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
    output = torch.empty_like(x)
    # launch triton kernel...
    return output
```

See `references/export-and-ops.md` for foreach_map and TorchScript deprecation details.

## Attention Ops

### varlen_attn() — Variable-Length Sequences (2.10)

```python
from torch.nn.attention.varlen import varlen_attn

# q, k, v are packed (total_tokens, num_heads, head_dim)
# cu_seqlens marks sequence boundaries: [0, seq1_len, seq1_len+seq2_len, ...]
output = varlen_attn(q, k, v, cu_seqlens_q, cu_seqlens_k, max_seqlen_q, max_seqlen_k)
# Supports forward + backward, torch.compile-able. Requires A100+, BF16/FP16.
```

### FlexAttention + FlashAttention-4 Backend (2.11)

FlexAttention on Hopper/Blackwell GPUs automatically uses FA4 kernels: 1.2x–3.2x speedup over Triton backend on compute-bound workloads. No code changes needed — automatic via `flex_attention()`.

See `references/attention.md` for details.

## Numerical Debugging — DebugMode (2.10)

```python
from torch.debugging import DebugMode

with DebugMode():
    output = model(x)
# Logs all dispatched ops with tensor hashes
# Compare hashes between two runs to find divergence point
```

## Deprecations & Compatibility

- **TorchScript** (2.10): Use `torch.export` instead of `torch.jit.script`/`torch.jit.trace`. Use ExecuTorch for embedded runtime.
- **FSDP1** (2.8): Use `fully_shard()` (FSDP2) instead of `FullyShardedDataParallel`.

### Environment

- **CUDA 13** is the default since 2.11. CUDA 12.8 builds available via `download.pytorch.org/whl/cu128`.
- **Python 3.14** supported since 2.10. Python 3.14t (free-threaded) experimentally supported.
- **Deterministic compile** (2.10): `torch.use_deterministic_algorithms(True)` now applies to torch.compile.

See `references/environment.md` for details on all compatibility changes.

## Reference Files

| File | Contents |
|------|----------|
| `torch-compile.md` | set_stance, mega cache, hierarchical compilation, control flow ops, error_on_graph_break, deterministic mode |
| `distributed-training.md` | FSDP2 fully_shard, context parallelism, symmetric memory, differentiable collectives, SafeTensors DCP |
| `export-and-ops.md` | Dim.AUTO, triton_op, TorchScript deprecation, foreach_map |
| `attention.md` | varlen_attn for packed sequences, FlexAttention + FA4 backend |
| `environment.md` | weights_only=True breaking change, CUDA 13 default, Python 3.14, DebugMode |
