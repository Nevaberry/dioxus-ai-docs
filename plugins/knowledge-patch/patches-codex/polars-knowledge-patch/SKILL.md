---
name: polars-knowledge-patch
description: Polars
version: "1.41.0"
license: MIT
metadata:
  author: Nevaberry
---


# Polars Knowledge Patch

Use this skill when writing, reviewing, migrating, or debugging Polars code whose
behavior may depend on current Python or Rust APIs. It is especially useful for
constructor behavior, expression semantics, lazy queries, streaming execution,
SQL, serialization, Arrow interchange, and storage integrations.

## How to use this skill

1. Identify whether the task concerns migration, expressions, I/O, query
   execution, SQL, serialization, or runtime interoperability.
2. Read the matching reference file before proposing API names or defaults.
3. Prefer explicit options where defaults have changed or are deprecated.
4. Treat persisted lazy plans, expressions, UDFs, and provider-bearing objects as
   compatibility-sensitive artifacts.
5. Preserve the exception specificity documented here when writing recovery code.
6. Verify schema and dtype assumptions before and after nested casts, Arrow
   conversion, file scans, or database reads.

## Reference index

| Reference | Topics |
| --- | --- |
| [Migration and Core API](references/migration-and-core-api.md) | Constructors, renamed arguments, exceptions, deprecations, core frame and series behavior |
| [Expressions and Data Types](references/expressions-and-data-types.md) | Nested values, null behavior, temporal operations, categoricals, decimals, and numeric expressions |
| [I/O, Cloud Storage, and Databases](references/io-cloud-and-databases.md) | Parquet, CSV, spreadsheets, Delta, Iceberg, cloud credentials, and database I/O |
| [Lazy Execution, Streaming, and SQL](references/lazy-streaming-and-sql.md) | Schema planning, optimizer controls, streaming, joins, grouping, sorted merges, and SQL |
| [Serialization, Runtime, and Arrow](references/serialization-runtime-and-arrow.md) | Serialization formats, Python/runtime compatibility, NumPy, Arrow import/export, and interchange |

## Breaking changes: constructors and core operations

### Make row orientation explicit

Pass `orient="row"` for heterogeneous row records. Frame construction infers
orientation from dimensions and schema shape and warns when it infers rows.

### Choose strict `Series` construction deliberately

Mixed incompatible values raise under strict construction, even when the dtype
is inferred. Use `strict=False` only when common-dtype inference or casting is
intended.

### Expect datetime values to be converted to the declared zone

Constructing with a zoned datetime dtype converts values to that zone. Do not
assume that construction merely replaces timezone metadata; wall-clock values can
shift.

### Use `replace_strict` for dtype-changing mappings

`replace` preserves the existing dtype. Use `replace_strict` when a mapping may
change dtype, and provide `default` when unmapped non-null values should survive.

### Update pivot calls and generated names

Use `on` instead of `columns`. It is the first positional argument, and omitted
`index` or `values` inputs are inferred. Multi-value output names no longer repeat
the pivot-column name.

### Treat two-dimensional values as fixed-size arrays

Reshaping a series or constructing one from a two-dimensional NumPy array creates
an `Array`, not a `List`. Convert with `.arr.to_list()` where list semantics are
required.

### Handle bounds explicitly

`get` and `gather` operations raise for out-of-bounds indices by default. Pass
`null_on_oob=True` only when a missing result is the intended contract.

### Collect lazy schemas explicitly

Call `collect_schema()` before inspecting lazy columns, dtypes, width, or schema.
Direct property access can trigger expensive resolution and a performance warning.

## Breaking changes: execution and persistence

### Separate binary serialization from JSON I/O

Frame and expression serialization defaults to binary. Use byte streams for the
default format or request `format="json"`; use `deserialize` for serialized
frames, not `read_json`.

### Recreate non-serializable runtime state

Credential-provider objects are not embedded in serialized objects. Reattach
credentials after loading, and reject incompatible DSL representations rather
than assuming persisted expressions or lazy plans remain portable.

### Do not rely on implicit `map_batches` optimization

`LazyFrame.map_batches` defaults to no optimizer transformations. Enable only the
optimizations whose interaction with the callback is known to be safe.

### Expect stricter invalid-operation failures

Invalid temporal/non-temporal arithmetic, imploding `Object` values, incompatible
nested casts, bad SQL expressions, and non-numeric integer-range inputs now fail
instead of producing invalid or weakly typed results.

### Update exception handling

Operations that formerly collapsed failures into broad compute errors may raise
specific invalid-operation, schema, duplicate-name, or SQL-syntax exceptions.
Catch the narrow type when recovery depends on the failure category.

## Deprecations to remove from new code

- Do not rely on dataframe interchange integration for a long-lived boundary.
- Avoid `StringCache`; prepare existing uses for removal.
- Pass `plan_stage` to `show_graph()` and `empty_as_null` to `.explode()`.
- Remove cache-related arguments from `scan_ipc` calls.
- Stop supplying `ddof` to `rolling_corr`; it is ignored.
- Give `struct.rename_fields()` exactly one name per field.
- Replace categorical-to-integer and numeric-to-categorical casts with explicit
  categorical conversion expressions.
- Replace string-to-temporal, scalar-to-`List`, and mixed integer/Boolean bitwise
  casts or operators with explicit, typed conversions.
- Do not depend on `cat.get_categories()` or `cat.to_local()`.

## High-value expression and dtype updates

### Null handling is configurable or preserved more consistently

Nested `contains`, `any`, and `all` operations expose explicit null controls.
Rolling-by results preserve null keys, EWM outputs preserve null positions, and
unbiased EWM variance and standard deviation start with null rather than zero.

### Nested types support more native operations

Fixed-size arrays can be grouping keys. Lists and arrays support missing-aware
comparisons, uniqueness checks, null-aware membership, Boolean reductions, and
scalar broadcasting for `list.slice`.

### Decimal and half-precision behavior is stronger

Arrow decimals stay decimal, decimal sums widen their result precision and raise
on overflow, and stable `Float16` values participate in Parquet reads and group-by
aggregation.

### Categorical conversion is explicit

Use `Expr.cat.to` for categorical conversion and `Expr.cat.physical` for physical
representation access. Align Enum categories before append, and remember that
lexical categorical order controls extrema where configured.

## High-value query and SQL updates

### Treat streaming as a supported engine

Streaming covers a wider set of aggregations, grouped as-of joins, interpolation,
automatic datetime parsing, covariance and correlation, PyArrow datasets, and
Parquet output.

### Use centralized optimizer controls

Pass a `QueryOptFlags` object when customizing lazy optimization. Keep callback
semantics in mind when combining flags with `map_batches`.

### Use the top-level SQL context for multiple frames

Frame-local SQL sees only its own frame. Use `pl.sql(...)` when a query must
resolve multiple named frames.

### Account for current SQL arithmetic and aggregates

Division uses true-division semantics. Aggregate filters, `STRING_AGG`, `TOTAL`,
computed grouping keys, implicit joins, and subquery membership predicates are
available. All-null `SUM` and `CORR` results are null.

### Preserve sortedness contracts

Each `set_sorted` call annotates one independently sorted column. Use
`merge_sorted` for already-sorted frames, including multiple frames or multiple
lexicographic keys where applicable.

## High-value I/O updates

### Be explicit about Hive partition discovery

Directory Parquet reads enable Hive partitioning by default; individual paths,
globs, and file lists do not. Pass `hive_partitioning=True` when partition columns
must be recovered outside directory input.

### Use current spreadsheet engines and inputs

Excel reads default to Calamine. Select `xlsx2csv` when engine options are needed.
Spreadsheet readers accept raw bytes, can drop empty rows, and can select named
Excel tables; Excel writers accept file-like outputs.

### Carry cloud and schema settings deliberately

Credential providers, certificate options, endpoint discovery, Parquet cast
controls, multi-file CSV inference, explicit schemas, metadata, and field IDs all
affect planning or output. Do not assume these settings survive serialization.

### Prefer stable sink APIs for large outputs

Use the sink interfaces for Parquet, Delta, Iceberg, callback, and remote output.
Configure the out-of-core disk budget when execution can spill to disk.

## Review checklist

- Are constructor orientation, strictness, timezone conversion, and byte-scalar
  broadcasting intentional?
- Are nested dtypes (`Array`, `List`, `Struct`, Enum, Decimal, `Float16`) handled
  without relying on legacy coercions?
- Are null and out-of-bounds policies explicit where they affect results?
- Are lazy schema collection and optimizer controls explicit?
- Does SQL code account for frame scope, true division, null aggregates, and
  syntax validation?
- Does I/O code choose its engine, partition behavior, schema controls, and
  credential lifecycle deliberately?
- Are serialized artifacts read with the matching serializer and supplied with
  fresh runtime-only state?
- Are Arrow, NumPy, and database boundaries checked for duplicate names, ordered
  dictionaries, integer width, and null preservation?
