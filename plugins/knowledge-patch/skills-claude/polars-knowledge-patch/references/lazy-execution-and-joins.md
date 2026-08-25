# Lazy execution and joins

Use this reference for lazy schemas and optimization, streaming execution,
windowing, joins, sorted merges, and sinks.

## Lazy schemas and optimization

### Explicit schema collection (1.0-upgrade)

Accessing `LazyFrame.schema`, `.dtypes`, `.columns`, or `.width` emits a
`PerformanceWarning` because resolving a lazy schema can be expensive. Collect
once and inspect the returned `Schema`:

```python
schema = lf.collect_schema()
columns = schema.names()
```

### Lazy schema matching (1.30.0)

`LazyFrame.match_to_schema` reconciles a lazy frame with an expected schema
before execution:

```python
lf = lf.match_to_schema({"id": pl.Int64})
```

### Centralized optimization flags (1.30.0)

Lazy optimization controls are centralized in `QueryOptFlags`. Code that
customizes optimization should pass that object instead of separate controls.

### Conservative `map_batches` defaults (1.40.0)

`LazyFrame.map_batches` defaults to no optimizations. Enable only the
transformations whose assumptions the callback satisfies; do not assume
optimizer transformations are implicit.

## Sortedness and merge operations

### One column per sortedness annotation (1.0-upgrade)

`set_sorted` accepts one column because each call promises that column is
individually sorted, not that several columns are jointly sorted. Annotate
independently sorted columns by chaining calls:

```python
df.set_sorted("a").set_sorted("b")
```

### Multi-frame sorted merges (1.40.0)

Top-level `pl.merge_sorted` merges multiple already-sorted frames.

### Multikey sorted merges (py-1.43.2-rs-0.55.1-0.55.2)

`merge_sorted` supports multiple merge keys for lexicographically sorted
frames. The input ordering must correspond to the complete key sequence.

## Join behavior

### Overlapping names in `join_where` (1.10.0)

`join_where` resolves columns whose names partially overlap.

### Exact-match control for as-of joins (1.20.0)

`join_asof` accepts `allow_exact_matches`, so equal keys can be excluded:

```python
left.join_asof(right, on="ts", allow_exact_matches=False)
```

### Grouped as-of joins in streaming (1.40.0)

The streaming engine supports grouped as-of joins. Grouped as-of joins also
preserve null rows rather than dropping them.

## Windows and grouping

### Index-count rolling windows (1.10.0)

`rolling_*_by` can define a window by index count as well as by time.

### Global window expressions (1.30.0)

Window expressions may call `.over()` without `partition_by`, treating the full
input as one window:

```python
df.with_columns(total=pl.col("value").sum().over())
```

### Keyless grouping (1.40.0)

`group_by()` accepts no key expressions, providing the group-by aggregation
interface for one global group.

## Streaming execution

### Additional aggregations and Parquet sink (1.20.0)

The new streaming engine executes first/last and additional `group_by`
aggregations and can write through the Parquet sink.

### Expanded operator coverage (1.40.0)

Streaming execution supports grouped as-of joins, native interpolation,
`strptime` with `format=None`, covariance and correlation, and PyArrow dataset
sources.

### Stable streaming engine (1.41.0)

The streaming engine is stable rather than experimental. Code that explicitly
selects it can treat it as a supported execution engine.

### Out-of-core spilling (py-1.43.2-rs-0.55.1-0.55.2)

Polars can spill out-of-core work to disk. Set `POLARS_OOC_DISK_BUDGET_MB` to
the disk budget in megabytes for that spilling.

## Sinks

### Stable sink APIs (1.30.0)

The `sink_*` APIs are stable rather than experimental.

### Unordered Delta sinks (1.40.0)

`sink_delta` no longer requires `maintain_order=True`; default ordering can be
used for Delta writes.

### Iceberg sink integration (1.40.0)

Polars provides an Iceberg sink DSL and callback for writing through the sink
interface.

### Parquet field IDs (1.40.0)

`sink_parquet` writes Parquet field IDs, preserving that schema information in
its output.

### Extensible callback sinks (py-1.43.2-rs-0.55.1-0.55.2)

Callback sinks can target cloud storage, while external `object_store`
implementations can provide schemes outside the native set.
