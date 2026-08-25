# Geometry operations

## Spatial indexing

`SpatialIndex.query` can return dense or sparse boolean arrays through
`output_format` (since 1.1.0). Sparse output requires SciPy.

```python
dense_hits = frame.sindex.query(queries.geometry, output_format="dense")
sparse_hits = frame.sindex.query(queries.geometry, output_format="sparse")
```

## Union and dissolve

`GeoSeries.union_all` and `GeoDataFrame.dissolve` accept `grid_size`
(since 1.1.0).

```python
merged = frame.geometry.union_all(grid_size=0.01)
dissolved = frame.dissolve("group", grid_size=0.01)
```

Both APIs also support the `disjoint_subset` union algorithm (since 1.1.0).

```python
merged = frame.geometry.union_all(method="disjoint_subset")
dissolved = frame.dissolve("group", method="disjoint_subset")
```

## Polygonal coverage operations

GeoSeries and GeoDataFrame expose coverage validation, invalid-edge reporting,
and topology-preserving coverage simplification (since 1.1.0).

```python
valid = frame.geometry.is_valid_coverage()
invalid_edges = frame.geometry.invalid_coverage_edges()
simplified = frame.geometry.simplify_coverage(0.5)
```

## Geometry repair

`make_valid` accepts `method` and `keep_collapsed` to select the repair
algorithm and whether to retain collapsed components (since 1.1.0).

```python
fixed = frame.geometry.make_valid(method="linework", keep_collapsed=True)
```

## Measured coordinates

Initial M-coordinate support provides `m`, `has_m`, and the `include_m` option
on `get_coordinates` (since 1.1.0).

```python
measures = points.m
has_measures = frame.geometry.has_m
coordinates = frame.geometry.get_coordinates(include_m=True)
```

## Geometry aggregation

`GroupBy.agg` supports named aggregations over a geometry column
(since 1.1.0).

## Point-pattern sampling

`GeoSeries.sample_points` accepts list-like `size` values with `pointpats`
methods, enabling per-geometry counts (since 1.1.3). Set `rng` to fix the
random state and make sampling reproducible.

```python
sampled = geometries.sample_points(
    size=[10, 20],
    method="cluster_poisson",
    rng=42,
)
```

Generated points are no longer sorted by x-coordinate (since 1.1.4). Do not
depend on their spatial ordering.
