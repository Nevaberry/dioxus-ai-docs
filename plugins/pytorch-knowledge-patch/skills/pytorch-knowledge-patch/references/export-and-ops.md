# Export & Custom Ops (2.6–2.7)

## Dim.AUTO for torch.export (2.6)

Automatically discover dynamic shapes without specifying them manually.

```python
from torch.export import export, Dim
ep = export(model, (x,), dynamic_shapes={"x": {0: Dim.AUTO}})
# Automatically infers min/max ranges, relations between dims, static/dynamic behavior
```

## torch.library.triton_op (2.6)

Register custom Triton kernels as operators that torch.compile can optimize through.

```python
@torch.library.triton_op("mylib::add", mutates_args=())
def add(x: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
    output = torch.empty_like(x)
    # launch triton kernel...
    return output
```

## TorchScript Deprecated (2.10)

Use `torch.export` instead of `torch.jit.script`/`torch.jit.trace`. Use ExecuTorch for embedded runtime.

## Foreach Map (2.7)

Apply any pointwise function to lists of tensors with horizontal fusion via torch.compile.

```python
# Instead of manual loops or limited torch._foreach_* ops:
@torch.compile
def update(params, grads, lr):
    torch._foreach_map(torch.add, params, grads, alpha=-lr)
```
