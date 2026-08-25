---
name: polars-knowledge-patch
description: Polars
version: 1.41.0
license: MIT
metadata:
  author: Nevaberry
---


# Polars Knowledge Patch

Use this skill when writing, reviewing, debugging, or migrating Polars code in
Python, Rust, or SQL. Check the project's pinned Polars version first and apply
only guidance relevant to that version. Prefer the project's schema, code, and
tests when they establish behavior more directly.

## Reference index

| Reference | Topics |
| --- | --- |
| [`data-types-and-expressions.md`](references/data-types-and-expressions.md) | Construction, dtypes, nested data, expressions, aggregation, temporal behavior |
| [`io-and-serialization.md`](references/io-and-serialization.md) | Parquet, Arrow, CSV, Excel, databases, cloud storage, serialization |
| [`lazy-execution-and-joins.md`](references/lazy-execution-and-joins.md) | Lazy schemas, optimizations, streaming, joins, grouping, sinks |
| [`migration-and-deprecations.md`](references/migration-and-deprecations.md) | Breaking defaults, renamed APIs, deprecations, exceptions, runtime support |
| [`sql.md`](references/sql.md) | SQL operators, functions, aggregates, joins, validation, frame scope |

## Migration triage

When upgrading an existing application, check these high-impact changes first:

1. Make row orientation explicit when constructing heterogeneous frames:

   ```python
   pl.DataFrame([[1, "a"], [2, "b"]], orient="row")
   ```

2. Expect inferred `Series` construction to be strict. Use `strict=False` only
   when common-dtype inference or casting is intentional.
3. Replace dtype-changing `replace` calls with `replace_strict`; supply a
   `default` when unmapped values must survive.
4. Read serialized frames with `deserialize`, not `read_json`. Default
   serialization is binary; request `format="json"` explicitly for JSON.
5. Audit Parquet path behavior. Directories enable Hive partitioning by default,
   while files, globs, and file lists do not.
6. Replace repeated lazy metadata access with one `collect_schema()` call.
7. Review SQL integer division: `/` uses true division and may return fractions.
8. Remove reliance on implicit optimization in `map_batches`; its default is no
   optimizer transformations.

## Construction and schema

### Build frames and series deliberately

- A zoned datetime dtype converts input values into its zone. It does not merely
  replace time-zone metadata, so naive wall-clock values may shift.
- Two-dimensional NumPy input and `Series.reshape` produce fixed-size `Array`
  values. Convert with `.arr.to_list()` when callers require `List`.
- Byte scalars in a `DataFrame` constructor broadcast across rows.
- Empty JSON construction preserves its schema.
- Duplicate names in an Arrow table, and duplicate names in a Parquet file,
  raise `DuplicateError`.
- Use `LazyFrame.match_to_schema(...)` to reconcile a lazy input with an expected
  schema before execution.

### Treat nested conversion as strict

`strict=True` validates conversions inside nested values, not only the outer
dtype. Align Enum category sets before appending; appending no longer merges
different category definitions.

For nested queries and transformations:

- `list.contains` and `arr.contains` accept `nulls_equal`.
- List and Array `any`/`all` accept `ignore_nulls`.
- List and Array support `is_unique`.
- Fixed-size Array columns can be grouping keys.
- `list.slice` broadcasts scalar input across rows.

## Expression behavior

### Handle nulls explicitly

- EWM mean, standard deviation, and variance preserve input null positions. Add
  `.forward_fill()` only when reproducing the earlier filled result.
- The initial unbiased `ewm_var` and `ewm_std` value is null.
- A null `clip` bound leaves the original value unchanged.
- `fill_null` operates on columns whose dtype is `Null`.
- Rolling-by expressions propagate nullness from their `by` column.

### Update selection and replacement code

- `pl.nth` positional arguments are indices. Use `pl.col("a").get(1)` to select
  an element from a named expression.
- `get` and `gather` raise for out-of-bounds indices unless
  `null_on_oob=True` is passed.
- `Series.equals` ignores names unless `check_names=True`.
- `replace_strict` supports Enum values and raises for unmapped non-null input
  when no default is supplied.

### Check changed numerical results

- Decimal sums widen result precision and raise instead of wrapping on overflow.
- Covariance with a constant returns zero rather than `NaN`.
- `rolling_corr` ignores its deprecated `ddof` argument.
- Globally seeded sampling is reproducible because `sample()` honors the global
  random seed.
- Datetime truncation is epoch-aligned; weekly buckets remain Monday-aligned.

## Lazy execution and streaming

### Collect schemas once

Access to `LazyFrame.schema`, `.dtypes`, `.columns`, and `.width` can trigger an
expensive schema resolution and warns accordingly. Prefer:

```python
schema = lf.collect_schema()
names = schema.names()
```

Use `QueryOptFlags` when customizing lazy optimization. Persisted expressions or
plans must use a DSL representation compatible with the reader; incompatible
representations are rejected.

### Use the streaming engine as supported execution

The streaming engine is stable and supports a broad set of operations, including
additional group-by aggregations, grouped as-of joins, native interpolation,
format-inferred `strptime`, covariance/correlation, PyArrow dataset sources, and
Parquet sinks. Grouped as-of joins preserve null rows.

Callback sinks can write cloud targets, and external `object_store`
implementations can add schemes beyond the native set. Configure
`POLARS_OOC_DISK_BUDGET_MB` to bound disk space for out-of-core spilling.

## I/O checkpoints

### Parquet and Arrow

- Unprojected Parquet columns are not dtype-validated during projected reads.
- Use `scan_parquet(..., cast_options=...)` to control scan-time casting.
- Parquet supports `Float16`, MAP columns without `LogicalType`, field and
  file-level metadata, IEEE 754 total-ordering metadata, and sink field IDs.
- Arrow decimals remain Decimal, chunked Arrow structs consume every chunk,
  Arrow map nulls survive import, and Enum exports are ordered dictionaries.
- PyArrow-backed `read_parquet` and `read_csv` support index-based column
  selection.

### Spreadsheets, CSV, and databases

- Excel defaults to `calamine`; choose `engine="xlsx2csv"` when engine options
  are required.
- Spreadsheet readers accept raw bytes and named Excel tables; Excel output can
  target file-like objects.
- Validate CSV schema overrides and configure multi-file inference with
  `infer_schema_files` where needed.
- ADBC append creates a missing destination table.
- Database reads can infer `Int128`.

## SQL checkpoints

- Frame methods query only their own frame. Use top-level `pl.sql(...)` for
  queries involving multiple frames.
- `/` is true division. Use an explicit operation when integer quotient behavior
  is required.
- Aggregate `FILTER`, `STRING_AGG`, `QUANTILE_DISC`, and `TOTAL` are available.
- `SUM` and `CORR` return null for all-null inputs.
- `LIKE` and `ILIKE` can span newline characters.
- Invalid `sql_expr` input and `HAVING` outside `GROUP BY` fail early.

## Deprecation checklist

Plan replacements for these interfaces:

- `StringCache`.
- dataframe interchange protocol integration.
- IPC scan cache arguments.
- `rolling_corr(ddof=...)`.
- implicit `show_graph()` plan stage and implicit `.explode()` empty handling.
- integer/Boolean bitwise mixing, string-to-temporal casts, and non-nested-to-
  `List` casts.
- numeric-to-Categorical and Categorical-to-integer casts, plus
  `cat.get_categories()` and `cat.to_local()`.
- mismatched name counts passed to `struct.rename_fields()`.

Use `Expr.cat.to` for explicit categorical conversion and `Expr.cat.physical`
for access to its physical representation. Follow PEP 702 diagnostics in static
analysis, since deprecated Polars APIs carry compatible annotations.

## Validation workflow

Before accepting a migration:

1. Pin and record the Polars version used by tests.
2. Assert schemas, not only row values, around Arrow, Parquet, JSON, Enum,
   Decimal, Array, and categorical boundaries.
3. Test lazy and streaming plans against representative nulls, empty inputs,
   duplicate names, and invalid casts.
4. Re-run SQL assertions involving division, null aggregates, literals, joins,
   multiline strings, and invalid syntax.
5. Round-trip serialization and remote I/O with the same engines and credential
   setup used in production.
6. Consult the topic references for exact option names, defaults, and versioned
   behavior before changing compatibility code.
