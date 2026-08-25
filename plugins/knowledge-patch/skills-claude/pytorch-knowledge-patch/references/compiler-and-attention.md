# Compiler and Attention

## Contents

- [Compiler compatibility and capture](#compiler-compatibility-and-capture)
- [Stances, graph breaks, and eager regions](#stances-graph-breaks-and-eager-regions)
- [Recompilation and dynamic shapes](#recompilation-and-dynamic-shapes)
- [Caching and repeated regions](#caching-and-repeated-regions)
- [Inductor backends and graph capture](#inductor-backends-and-graph-capture)
- [Compiled control flow and foreach map](#compiled-control-flow-and-foreach-map)
- [FlexAttention backends](#flexattention-backends)
- [Score modifications and sparse masks](#score-modifications-and-sparse-masks)
- [Autograd and distributed boundaries](#autograd-and-distributed-boundaries)
- [Determinism and numerical debugging](#determinism-and-numerical-debugging)

## Compiler compatibility and capture

TorchDynamo gained exception handling and `MutableMapping` capture in 2.5.0.
The CPU Inductor backend also became a Windows prototype supporting MSVC
(`cl`), Clang (`clang-cl`), and Intel (`icx-cl`), while eager and the C++
Inductor backend gained prototype CPU `float16` execution.

`torch.compile` supports Python 3.13 since 2.6.0 and Python 3.14 since 2.10.0;
free-threaded Python 3.14t support is experimental. Since 2.7.0 it can capture
Torch Function Modes, so `torch.*` overrides and backend-specific rewrites can
participate in compiled execution.

The 2.11.0 capture surface adds `contextlib.ExitStack`,
`contextlib.suppress`, module hooks using `kwargs=True`, and backward hooks on
intermediate tensors. Initial API-unstable
`torch._dynamo.decorators.leaf_function` support keeps marked functions opaque
to Dynamo and AOTAutograd. Add logging-only callables to
`torch._dynamo.config.ignore_logging_functions` to skip them as side effects.

## Stances, graph breaks, and eager regions

Since 2.6.0, `torch.compiler.set_stance()` controls behavior across invocations
of compiled functions. For example, `"eager_on_recompile"` reuses cached
compiled code but runs eagerly when a new specialization would otherwise need
compilation:

```python
torch.compiler.set_stance("eager_on_recompile")
```

The API-unstable `torch._dynamo.error_on_graph_break()` introduced in 2.9.0
makes graph breaks errors only inside a selected context or decorated function.
Unlike `fullgraph=True`, code can later resume ordinary break-and-continue
behavior:

```python
@torch.compile
def f(x):
    with torch._dynamo.error_on_graph_break():
        return x.sin()
```

Use `torch.compiler.disable()` around a region that must remain eager. With
`fullgraph=True` in 2.11.0, compiled execution recursively disables Dynamo to
prevent accidental nested compilation.

## Recompilation and dynamic shapes

`torch.compile` specializes non-tensor arguments and non-tensor globals.
Tensor sizes start static; after the first size-driven recompile, Dynamo tries
to generalize them dynamically. Fail rather than silently recompiling when
auditing a workload:

```python
torch._dynamo.config.error_on_recompile = True
```

Set `TORCH_DYNAMO_AUTOMATIC_DYNAMIC_SHAPES=0` to disable Dynamo's automatic
dynamic-shape generalization globally (2.11.0). The configurable Triton
compilation timeout now defaults to five minutes.

## Caching and repeated regions

Mega Cache added portable end-to-end `torch.compile` cache artifacts in 2.7.0.
Compile and run the workload first, call
`torch.compiler.save_cache_artifacts()`, then call
`torch.compiler.load_cache_artifacts()` in another process or on another
machine to pre-populate all included caches.

Since 2.8.0, marking structurally repeated operation blocks with
`nested_compile_region` compiles the nested region once and reuses its generated
code. This reduces compiler work for repeated stacks such as transformer
layers.

## Inductor backends and graph capture

Enable AOTInductor freezing for CPU graphs containing MKLDNN operators with
opaque serialized weights (since 2.4.0):

```sh
export TORCHINDUCTOR_FREEZING=1
```

AOTInductor's C++ runtime added CUTLASS and CK GEMM autotuning choices in 2.6.0,
including dynamic-shape support and kernel-binary compilation reuse. In 2.8.0,
the CUTLASS backend also became available to `torch.compile`, covering `mm`,
FP8 `mm`, `addmm`, and `bmm`.

Inductor CUDAGraph partitioning (2.8.0) splits around uncapturable operations
such as CPU work, device copies, and CUDAGraph-unsafe custom operators. It
reorders work to reduce partition count and captures each compatible CUDA-only
partition separately.

For compiler bisection in 2.11.0, assign graph-number ranges to alternate
backends:

```sh
TORCH_COMPILE_OVERRIDE_BACKENDS='0-5:aot_eager;6-10:inductor' python app.py
```

## Compiled control flow and foreach map

Foreach Map (2.7.0) uses `torch.compile` to apply built-in pointwise operations
or user Python functions across lists of tensors. It accepts mixtures of scalar
values and tensor lists and produces a horizontally fused kernel.

The API-unstable compiled control-flow library added `cond`, `while_loop`,
`scan`, `associative_scan`, and `map` in 2.8.0 for tensor-dependent branches,
loops, and dynamic-shape flow in compiled or exported programs. These operators
target inference and export. Training is supported except for `while_loop` in
2.8.

## FlexAttention backends

FlexAttention runs on x86 CPUs through Inductor's C++ backend since 2.6.0,
including composed variants such as PageAttention for CPU LLM inference.

The 2.7.0 decoding backend added inference with grouped-query attention,
PagedAttention, nested jagged tensors, and trainable biases. API-unstable
forward and backward support arrived for Intel GPUs in 2.9.0 without requiring
device-specific FlexAttention code.

In 2.11.0, API-unstable FlexAttention can use a FlashAttention-4 backend on
Hopper and Blackwell. It emits CuTeDSL score and mask modifications and
JIT-instantiates kernels. It also supports deterministic mode, compiled Q with
lower-precision K/V, and BlockSparse backward with dynamic shapes and backward
score modifications.

## Score modifications and sparse masks

`flex_attention()` accepts a scalar
`score_mod(score, b, h, q_idx, kv_idx)` callable. It fuses the callable before
softmax, generates its backward, and permits captured tensors such as per-head
biases:

```python
from torch.nn.attention.flex_attention import flex_attention

def relative_bias(score, b, h, q_idx, kv_idx):
    return score + q_idx - kv_idx

output = flex_attention(query, key, value, score_mod=relative_bias)
```

For sparse attention, define `mask_mod(b, h, q_idx, kv_idx)` and create a
`BlockMask`. Returning `-inf` from `score_mod` is numerically correct but cannot
skip masked blocks. Use `B=None` or `H=None` when a pattern is shared across
that dimension. A mask and a score modification can be used together.

```python
from torch.nn.attention.flex_attention import create_block_mask

def causal(b, h, q_idx, kv_idx):
    return q_idx >= kv_idx

block_mask = create_block_mask(
    causal,
    B=None,
    H=None,
    Q_LEN=query.size(-2),
    KV_LEN=key.size(-2),
    _compile=True,
)
output = flex_attention(query, key, value, block_mask=block_mask)
```

Changing a tensor captured by a score or mask callable does not itself require
a FlexAttention kernel recompile. Recompute `BlockMask` whenever the tensor
changes the sparsity pattern. Cache an invariant mask globally; build a
per-batch mask, such as packed-document attention, once near the start of the
network and reuse it across layers. Do not wrap `create_block_mask()` directly
in `torch.compile()`; `_compile=True` reduces its construction time and peak
memory.

## Autograd and distributed boundaries

Compiled functions compose with eager autograd, DDP, and FSDP, with these
limits:

- Double backward is unsupported.
- Tensor subclasses require explicit compiler support.
- Differentiating with respect to an intermediate returned by a compiled region
  does not work.
- Eager autograd materializes gradients only at the end of a compiled region.
  Streaming them earlier requires compiled autograd and a fully compilable
  backward.

`torch.compile` can capture c10d collectives and DTensor programs but does not
optimize the collectives or assume SPMD execution by default. Compilation is
normally independent on every rank. Keep inputs and compiler decisions
consistent, because rank-specific recompilation can desynchronize ranks and
lead to NCCL timeouts.

## Determinism and numerical debugging

Since 2.10.0, compiled execution honors deterministic algorithms. Enable them
before compiling:

```python
torch.use_deterministic_algorithms(True)
compiled_model = torch.compile(model)
```

For FP16/BF16 numerical investigations, request eager-style precision casts:

```python
torch._inductor.config.emulate_precision_casts = True
```

This restores down/up-casts that fusion can remove, but compiled and eager
results may still differ because of matrix-multiplication implementations and
reduction order.

The API-unstable `DebugMode` (2.10.0) is a `TorchDispatchMode` that records
dispatched operations and Inductor-generated Triton kernels, attaches
deterministic hashes to tensor inputs and outputs, and accepts custom dispatch
hooks. Compare hashes from equal-input runs to find the first operation where
numeric results diverge.
