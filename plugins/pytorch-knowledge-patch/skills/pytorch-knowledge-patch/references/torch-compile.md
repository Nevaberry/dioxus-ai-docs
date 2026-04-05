# torch.compile Improvements (2.6–2.10)

## torch.compiler.set_stance (2.6)

Control torch.compile behavior between invocations without recompilation.

```python
with torch.compiler.set_stance("eager_on_recompile"):
    # Runs eagerly when recompilation needed, uses cached compiled code when possible
    result = compiled_fn(x)

# Other stances: "default", "force_eager"
```

## Mega Cache — Portable Compilation Artifacts (2.7)

Save/load compilation artifacts for portable caching across machines.

```python
# After compiling and running:
artifacts = torch.compiler.save_cache_artifacts()
# Save artifacts to disk/storage...

# On another machine or later run:
torch.compiler.load_cache_artifacts(artifacts)
# Subsequent torch.compile calls will use cached artifacts
```

## Hierarchical Compilation (2.8)

Compile repeated blocks once and reuse, reducing compile time for LLMs.

```python
@torch.compile
def model_forward(x):
    for layer in layers:
        with torch.compiler.nested_compile_region():
            x = layer(x)  # Compiled once, reused for all layers
    return x
```

## Control Flow Operators for compile/export (2.8)

Five operators for data-dependent control flow without graph breaks: `cond`, `while_loop`, `scan`, `associative_scan`, `map`.

```python
from torch._higher_order_ops.cond import cond
from torch._higher_order_ops.while_loop import while_loop
from torch._higher_order_ops.scan import scan

# cond: data-dependent branching
result = cond(pred_tensor, true_fn, false_fn, operands)

# scan: sequential reduction over a dimension (like jax.lax.scan)
carry, outputs = scan(combine_fn, init_carry, xs)

# associative_scan: parallel-friendly scan
from torch._higher_order_ops.scan import associative_scan
result = associative_scan(combine_fn, xs, dim=0)
```

## error_on_graph_break() Context Manager (2.9)

Toggle graph break behavior in specific regions (unlike fullgraph which is all-or-nothing).

```python
with torch._dynamo.error_on_graph_break():
    # torch.compile will error (not silently break) on graph breaks here
    compiled_fn(x)
# Outside the context, graph breaks resume silently as usual
```

## Deterministic Mode for torch.compile (2.10)

`torch.use_deterministic_algorithms(True)` now applies to torch.compile. Two invocations with the same input produce identical results.
