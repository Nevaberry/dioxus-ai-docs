# Export, AOTInductor, and Custom Operators

## Contents

- [Choose strict or non-strict export](#choose-strict-or-non-strict-export)
- [Specify dynamic shapes](#specify-dynamic-shapes)
- [Constrain data-dependent values](#constrain-data-dependent-values)
- [Represent control flow](#represent-control-flow)
- [Choose export IR](#choose-export-ir)
- [Inspect dynamic-shape failures](#inspect-dynamic-shape-failures)
- [AOTInductor artifacts and packaging](#aotinductor-artifacts-and-packaging)
- [ONNX export capabilities](#onnx-export-capabilities)
- [Compiler-aware custom operators](#compiler-aware-custom-operators)

## Choose strict or non-strict export

`torch.export.export(..., strict=False)` traces by executing through the Python
interpreter, so ordinary Python constructs rejected by strict Dynamo analysis
may pass. Non-tensor operations are not recorded, however: their trace-time
results can be frozen into the graph. Inspect the `ExportedProgram` for
accidental specialization.

```python
ep = torch.export.export(model, example_args, strict=False)
print(ep)
```

## Specify dynamic shapes

Since 2.6.0, `Dim.AUTO` lets export infer minimum and maximum ranges,
relationships between dimensions, and whether each dimension is static or
dynamic. Choose markers according to the intended contract:

- `Dim.AUTO` permits either dynamism or specialization.
- `Dim.DYNAMIC` requires a dimension to remain dynamic and raises if tracing
  forces it constant.
- `Dim.STATIC` explicitly specializes a dimension.

A sample size of 0 or 1 specializes even when marked `AUTO`, because those
sizes have non-generalizable behavior such as broadcasting. Use a sample size
greater than 1 when a dimension must vary.

At the input level, `None` makes every tensor dimension static and is required
for non-tensor inputs. Dimension-level `None` is deprecated; use `Dim.STATIC`.
An integer dimension specification is static and also validates the sample
against that integer.

```python
from torch.export.dynamic_shapes import Dim

ep = torch.export.export(
    model,
    (x,),
    dynamic_shapes={"x": (Dim.DYNAMIC, Dim.STATIC)},
)
```

Named dimensions form checked shape contracts. Reusing one requires equality.
A derived dimension may be a univariate linear expression `A * dim + B`; a
dimension specified as `4 * d` therefore also requires divisibility by four.

```python
d = Dim("d", min=4, max=256)
h = Dim("h", max=512)
dynamic_shapes = {
    "x": (d, Dim.STATIC),
    "y": (2 * d, h),
}
ep = torch.export.export(model, (x, y), dynamic_shapes=dynamic_shapes)
```

Export raises `ConstraintViolation` when tracing proves the contract
impossible. Its suggested fixes can make a dimension constant or replace one
named dimension with another.

## Constrain data-dependent values

Values produced by `item()`, `tolist()`, or `unbind()` can remain in an export
graph as unbacked symbols. Export fails when an unknown value is needed for a
Python branch or to prove an operation valid. `torch._check()` both emits a
runtime assertion and supplies equality or range facts to the symbolic-shape
solver:

```python
def forward(self, index, values):
    i = index.item()
    torch._check(i >= 0)
    torch._check(i < values.shape[0])
    return values[i]
```

Checks can relate an unbacked value to a shape or constant, refine lower and
upper bounds, and prove a branch condition. Bounds appear in the exported
program's `range_constraints`.

Avoid explicit `int(symbolic_value)` and implicit concretization such as
`range(symbolic_value)`. Both require a trace-time integer and can cause a
specialized-integer export failure. Prefer tensor operations accepting the
symbolic value, or use `torch._check(value == constant)` only for deliberate
specialization.

```python
def forward(self, count, y):
    n = count.item()
    return y.unsqueeze(0).repeat(n, 1) + n
```

## Represent control flow

Replace data-dependent Python `if` statements with `torch.cond`. Its predicate
must be a Boolean or one-element tensor. Operands must be tensors; both branches
must match the operand signature and return one tensor with identical metadata.
Branches cannot mutate inputs or globals or capture closure variables other
than `self`.

```python
def forward(self, x):
    return torch.cond(
        x.sum() > 0,
        lambda x: torch.sin(x),
        lambda x: torch.cos(x),
        [x],
    )
```

The API-unstable control-flow library introduced for compiled and exported
programs in 2.8.0 also provides `while_loop`, `scan`, `associative_scan`, and
`map`. These cover tensor-dependent loops and dynamic-shape flow. They target
inference and export; training works except for `while_loop` in 2.8.

## Choose export IR

The generic ATen IR returned by `export()` may contain mutation and aliasing and
can be trained through eager autograd. Run decompositions with an empty table
to functionalize without further lowering:

```python
functional_ep = ep.run_decompositions(decomp_table={})
```

Use `default_decompositions()` to lower toward the smaller Core ATen operator
set for backends:

```python
from torch.export import default_decompositions

table = default_decompositions()
table[torch.ops.aten.conv2d.default] = custom_conv_lowering
core_aten_ep = ep.run_decompositions(decomp_table=table)
```

The table is mutable; assign a callable to an operator key before passing it to
`run_decompositions()` to override that lowering.

## Inspect dynamic-shape failures

Enable dynamic logs to see symbol creation, operation guards, and the user lines
that emitted them:

```sh
TORCH_LOGS='+dynamic' python export_model.py
TORCHDYNAMO_EXTENDED_DEBUG_GUARD_ADDED='Eq(s0, s1)' python export_model.py
```

Use `torch._logging.set_logs(dynamic=10)` interactively. Copy one guard into
`TORCHDYNAMO_EXTENDED_DEBUG_GUARD_ADDED` for deeper attribution. Export errors
may recommend `draft_export()` to collect a broader set of failures before
fixing the program.

## AOTInductor artifacts and packaging

The PT2 archive format introduced in 2.6.0 is a zip containing everything
needed to consume an AOTInductor artifact in another environment. One archive
can contain multiple programs and additional metadata. The AOTInductor minifier
can reduce an API failure to a minimal reproducing `nn.Module`.

ABI-compatible code generation restricts output to stable C interfaces in
libtorch, allowing an AOTInductor artifact to continue running with newer
PyTorch versions. The C++ runtime can choose dynamic-shape CUTLASS and CK GEMM
autotuning kernels without compiling duplicate kernel binaries.

API-unstable helpers compile an `ExportedProgram` into a PT2 package and load it
for Python execution. The loaded callable takes tensor inputs as a list:

```python
import torch._inductor

with torch.no_grad():
    package = torch._inductor.aoti_compile_and_package(ep)

compiled = torch._inductor.aoti_load_package(package)
result = compiled([input_tensor])
```

Intel GPUs gained AOTInductor and `torch.export` deployment on Linux in 2.7.0,
including full-graph PT2E post-training quantization pipelines. In 2.11.0, XPU
adds AOTInductor standalone compilation and multi-architecture kernel paths.

## ONNX export capabilities

In 2.11.0, exported programs can serialize nested tensors. RNN modules,
including LSTM and GRU, can export on GPUs, and LSTM tracing supports dynamic
shapes.

The ONNX exporter also adds `ExportableModule` and `InputObserver` for inferring
dynamic shapes, including forcing the leading dimension dynamic and providing
custom shapes for empty tensors. It can export `while_loop` and
`invoke_subgraph`. After export, use `ONNXProgram.rename_axes()` to rename
dimensions.

For removed ONNX arguments and translation-table changes, read
[migrations-and-security.md](migrations-and-security.md#onnx-exporter-migrations).

## Compiler-aware custom operators

Since 2.6.0, wrap a user-defined Triton kernel with `torch.library.triton_op` so
it has a standard custom-operator boundary while remaining visible to
`torch.compile` for inspection and optimization.

In 2.11.0, `check_out_variant` checks whether a custom operator's out variant is
compatible with Inductor's out-variant pass. `to_out_variant` resolves an
`OpOverload` to the corresponding out variant.
