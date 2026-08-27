# Migration and deprecations

Use this reference for upgrade-sensitive defaults, renamed interfaces,
exception changes, runtime requirements, and deprecation cleanup.

## Constructor and transformation migrations

### Strict inference and explicit orientation (1.0-upgrade)

`Series` construction is strict for inferred and declared dtypes. Use
`strict=False` only when common-dtype inference or explicit-dtype casting is
intentional. `DataFrame` row inference is dimension-based and warns; pass
`orient="row"` for heterogeneous row records.

### Zoned datetime conversion (1.0-upgrade)

A zoned datetime dtype converts values to its time zone rather than replacing
metadata. Audit code that expects naive wall-clock values to remain unchanged.

### Array instead of List (1.0-upgrade)

Two-dimensional NumPy construction and `Series.reshape` produce fixed-size
`Array`. Convert with `.arr.to_list()` when downstream code requires `List`.

### Replacement API split (1.0-upgrade)

`replace` preserves dtype, while dtype-changing mappings belong in
`replace_strict`. The `default` and `return_dtype` parameters on `replace` are
deprecated.

## Pivot migrations

### Argument and output-name changes (1.0-upgrade)

`DataFrame.pivot` renamed `columns` to `on`, made `on` the first positional
argument, and made `index` and `values` optional by inferring remaining
columns. With multiple value columns, output names omit the redundant pivot
column: a name such as `test_1_subject_maths` becomes `test_1_maths`.

### Null pivot keys (1.40.0)

`pivot` retains data whose `on` value is null.

## Exceptions and validation

### More specific operation exceptions (1.0-upgrade)

Failures previously surfaced as `ComputeError` may raise
`InvalidOperationError` or `SchemaError`. Update exception handling around
casts and schema-dependent operations.

### Python exceptions retain identity (1.30.0)

Python exceptions crossing Polars execution preserve their original exception
type and traceback, so specific handlers and diagnostics remain usable.

### Duplicate schema errors (1.20.0)

Constructing from a PyArrow table with duplicate names raises `DuplicateError`.
Parquet files with duplicate names likewise raise `DuplicateError` (1.41.0).

### Strict nested casts (1.30.0)

`strict=True` validates inner nested values as well as the outer dtype. Expect
invalid inner conversions to raise.

### Invalid ranges and SQL expressions (1.40.0)

`pl.int_ranges` raises on non-numeric input. `sql_expr` rejects invalid input
instead of allowing it through.

### Strict temporal and object operations (py-1.43.2-rs-0.55.1-0.55.2)

Adding or subtracting temporal and non-temporal series raises. Imploding an
`Object` series raises instead of creating an invalid `List(Object)`.

## Python and dependency requirements

### Python runtime floor (1.10.0)

Python 3.9 is the oldest supported Python version.

### Python 3.13 support (1.20.0)

Python 3.13 is an officially supported runtime.

### Renamed installation extras (1.0-upgrade)

Update installations that request `fastexcel`, `gevent`, `matplotlib`, or
`async`. The documented replacement for
`polars[fastexcel,gevent,matplotlib]` is `polars[calamine,async,graph]`.

## Renamed and changed APIs

### RLE fields (1.0-upgrade)

Use `len` and `value` instead of `lengths` and `values` in the struct returned
by `rle`. The `len` field uses the unsigned index dtype (`UInt32` by default),
not `Int32`.

### Positional `pl.nth` (1.0-upgrade)

Every positional input to `pl.nth` is an index; the old `columns` behavior is
gone. Use `pl.col("a").get(1)` for a row from a named expression.

### Name-insensitive equality (1.0-upgrade)

`Series.equals` ignores names by default. Add `check_names=True` when names are
semantically significant.

### Unique dummy names (1.10.0)

`Series.to_dummies` no longer emits duplicate column names.

### Singular line-reader output (1.40.0)

The implicit output name from `scan_lines` and `read_lines` is `line` rather
than `lines`.

## Deprecations

### PEP 702 annotations (1.30.0)

Deprecated Polars APIs participate in PEP 702 behavior, allowing compatible
static-analysis tools to identify their use.

### Dataframe interchange protocol (1.40.0)

Polars' dataframe interchange protocol integration is deprecated. Treat
integrations depending on it as transitional.

### IPC scan cache controls (1.40.0)

Cache-related arguments of `scan_ipc` are deprecated and should not be relied
on.

### Rolling correlation degrees of freedom (1.40.0)

`rolling_corr` ignores and deprecates `ddof`; supplying it no longer affects the
result.

### `StringCache` (1.41.0)

`StringCache` is deprecated. Avoid new dependencies and prepare existing uses
for removal.

### Explicit graph and explode choices (py-1.43.2-rs-0.55.1-0.55.2)

Calling `show_graph()` without `plan_stage`, or `.explode()` without
`empty_as_null`, is deprecated. Pass both choices explicitly.

### Categorical migrations (py-1.43.2-rs-0.55.1-0.55.2)

The following are deprecated:

- casting `Categorical` values to integer dtypes;
- casting numeric values to `Categorical`;
- `cat.get_categories()`; and
- `cat.to_local()`.

Use `Expr.cat.to` for explicit conversion and `Expr.cat.physical` for the
physical representation.

### Cast and operator deprecations (py-1.43.2-rs-0.55.1-0.55.2)

String-to-temporal casts, casts from non-nested dtypes to `List`, and bitwise
operations between integer and Boolean values are deprecated. Convert inputs
explicitly before the temporal, list, or bitwise operation.

### Struct rename arity (py-1.43.2-rs-0.55.1-0.55.2)

Calling `struct.rename_fields()` with a different number of names than fields
is deprecated. Supply exactly one name per field.

### Arrow stream conversion path (py-1.43.2-rs-0.55.1-0.55.2)

`from_arrow` emits `FutureWarning` for an input implementing
`ArrowStreamExportable`; plan for that conversion path to change.

## Migration verification

After an upgrade, exercise constructor strictness, schema assertions, null and
out-of-bounds cases, persisted plans, and selected I/O backends. Run static
analysis to surface PEP 702 deprecations, and make every new graph, explode,
categorical, temporal, list, and mixed-bitwise choice explicit.
