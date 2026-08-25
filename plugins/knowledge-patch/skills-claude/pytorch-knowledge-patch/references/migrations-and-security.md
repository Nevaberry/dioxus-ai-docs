# Migrations and Security

## Contents

- [Safe checkpoint loading](#safe-checkpoint-loading)
- [Repository trust](#repository-trust)
- [TorchScript and export migrations](#torchscript-and-export-migrations)
- [ONNX exporter migrations](#onnx-exporter-migrations)
- [PT2E moves to TorchAO](#pt2e-moves-to-torchao)
- [Variable-length attention migration](#variable-length-attention-migration)
- [CUDA linear algebra routing](#cuda-linear-algebra-routing)

## Safe checkpoint loading

Since 2.6.0, `torch.load()` defaults to `weights_only=True`. The restricted
unpickler does not import modules or call arbitrary functions and permits only
the allowlisted types needed for plain-tensor `state_dict` files.

```python
state_dict = torch.load("weights.pt")
model.load_state_dict(state_dict)
```

Whole serialized `nn.Module` instances fail under this default. Load a legacy
pickle with `weights_only=False` only when its source and contents are trusted,
because pickle loading can execute code:

```python
trusted_module = torch.load("legacy-module.pt", weights_only=False)
```

Tensor subclasses, NumPy arrays, and other non-default objects can remain on
the restricted path by iteratively allowlisting the types named in the load
error. Scope an allowlist with `torch.serialization.safe_globals(...)` or add
it with `add_safe_globals(...)`. TorchFix can locate `torch.load` call sites
that omit `weights_only`, allowing an upgrade audit before behavior changes.

## Repository trust

Since 2.11.0, `torch.hub.list()`, `torch.hub.load()`, and `torch.hub.help()`
default `trust_repo` to `"check"`. PyTorch prompts before executing code from
an untrusted repository. `trust_repo=None` has been removed.

Non-interactive callers must choose an explicit policy. Pass `True` only after
establishing that the repository is trusted:

```python
model = torch.hub.load("user/repo", "model", trust_repo=True)
```

## TorchScript and export migrations

TorchScript is deprecated as of 2.10.0. Use `torch.export` for new export
workflows.

`torch.export.export_for_training()` was removed in 2.11.0. Replace it with
`torch.export.export()`, which now produces the same graph previously returned
by the training-specific entry point.

## ONNX exporter migrations

In 2.11.0, `torch.onnx.export()` no longer accepts `fallback`. If a caller must
retain the legacy exporter, catch failure from the dynamo exporter and call the
legacy path explicitly rather than requesting automatic fallback.

Each `custom_translation_table` operator value must now be one callable, not a
sequence of overload candidates. Put any type dispatch inside that callable:

```python
custom_translation_table = {
    torch.ops.aten.logical_and.default: custom_impl,
}
torch.onnx.export(
    model,
    args,
    "model.onnx",
    dynamo=True,
    custom_translation_table=custom_translation_table,
)
```

## PT2E moves to TorchAO

In 2.11.0, core PyTorch removed `torch.ao.quantization.pt2e` and
`torch.ao.quantization.quantizer`, including quantizers, specifications,
annotations, graph utilities, and the numeric debugger. Install TorchAO and use
the replacements under `torchao.quantization.pt2e`:

```python
from torchao.quantization.pt2e import prepare_pt2e, convert_pt2e
from torchao.quantization.pt2e.quantizer.x86_inductor_quantizer import (
    X86InductorQuantizer,
)
```

## Variable-length attention migration

The API-unstable `torch.nn.attention.varlen_attn()` added BF16/FP16 forward and
backward support under `torch.compile` in 2.10.0 for NVIDIA A100-or-newer GPUs
using the FlashAttention 2 backend.

Its 2.11.0 signature makes every optional argument keyword-only, adds the
softmax `scale`, and replaces `is_causal` with `window_size`:

- `(-1, -1)` selects full attention.
- `(-1, 0)` selects causal attention.
- `(W, 0)` selects causal sliding-window attention of size `W`.

```python
output = varlen_attn(
    query,
    key,
    value,
    cu_seq_q,
    cu_seq_k,
    max_q,
    max_k,
    window_size=(-1, 0),
    scale=1.0,
)
```

## CUDA linear algebra routing

Selecting MAGMA through
`torch.backends.cuda.preferred_linalg_library("magma")` is deprecated as of
2.11.0. On CUDA, routing is now fixed for these operations regardless of the
preference:

- `torch.linalg.svd()` and `torch.linalg.lstsq()` always use cuSOLVER.
- `torch.linalg.solve_triangular()` and the legacy `triangular_solve()` always
  use cuBLAS.
