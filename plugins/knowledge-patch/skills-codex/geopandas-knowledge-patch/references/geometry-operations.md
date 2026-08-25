# Geometry Operations

## Spatial-index boolean output

Since 1.1.0, `SpatialIndex.query` accepts `output_format="dense"` and
`output_format="sparse"` for boolean-array results:

```python
dense_hits = frame.sindex.query(
    queries.geometry,
    output_format="dense",
)
sparse_hits = frame.sindex.query(
    queries.geometry,
    output_format="sparse",
)
```

Sparse output requires SciPy.

## Precision-grid unions

Since 1.1.0, `GeoSeries.union_all` and `GeoDataFrame.dissolve` accept
`grid_size`:

```python
merged = frame.geometry.union_all(grid_size=0.01)
dissolved = frame.dissolve("group", grid_size=0.01)
```

The grid size controls the precision grid used by the union operation.

## Disjoint-subset union method

Since 1.1.0, both union entry points also accept the `disjoint_subset`
algorithm:

```python
merged = frame.geometry.union_all(method="disjoint_subset")
dissolved = frame.dissolve("group", method="disjoint_subset")
```

Pass the method explicitly rather than assuming it is selected automatically.

## Polygonal coverage operations

GeoSeries and GeoDataFrame provide three related coverage operations since
1.1.0:

```python
valid = frame.geometry.is_valid_coverage()
invalid_edges = frame.geometry.invalid_coverage_edges()
simplified = frame.geometry.simplify_coverage(0.5)
```

- `is_valid_coverage()` validates the polygonal coverage.
- `invalid_coverage_edges()` reports edges responsible for invalidity.
- `simplify_coverage(tolerance)` simplifies while preserving coverage
  topology.

## Configurable geometry repair

Since 1.1.0, `make_valid` accepts `method` and `keep_collapsed`:

```python
fixed = frame.geometry.make_valid(
    method="linework",
    keep_collapsed=True,
)
```

Use `method` to select the repair algorithm. Use `keep_collapsed` to control
whether components that collapse during repair remain in the result.

## Measured-coordinate support

Initial M-coordinate support in 1.1.0 adds:

- the `m` property for measure values;
- the `has_m` property for testing measured coordinates;
- `include_m=True` on `get_coordinates`.

```python
measures = points.m
has_measures = frame.geometry.has_m
coordinates = frame.geometry.get_coordinates(include_m=True)
```
