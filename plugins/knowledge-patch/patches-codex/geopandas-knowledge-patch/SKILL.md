---
name: geopandas-knowledge-patch
description: GeoPandas
version: "1.1.4"
license: MIT
metadata:
  author: Nevaberry
---


# GeoPandas Knowledge Patch

## When to use this skill

Load this skill when working on GeoPandas code involving:

- dependency compatibility and optional integrations;
- spatial indexes, unions, precision grids, or polygonal coverages;
- geometry repair, measured coordinates, or coordinate extraction;
- Arrow, Parquet, Feather, feature, file, or PostGIS I/O;
- pandas interoperability, grouping, missing values, or geometry-column state;
- overlays, point sampling, or interactive map legends.

Use the quick reference for common decisions; open the topic reference when exact API detail matters.

## Reference index

| Reference | Topics |
| --- | --- |
| [compatibility.md](references/compatibility.md) | Runtime and optional-dependency floors |
| [geometry-operations.md](references/geometry-operations.md) | Spatial-index outputs, unions, coverages, repair, and M coordinates |
| [io-and-databases.md](references/io-and-databases.md) | Arrow conversion, feature and file input, missing strings, and PostGIS |
| [pandas-integration.md](references/pandas-integration.md) | Accessors, aggregation, geometry state, CRS, missing geometry, and removed methods |
| [overlays-sampling-and-maps.md](references/overlays-sampling-and-maps.md) | Overlay edge cases, sampling controls and order, and explore legends |

## Breaking changes and deprecations

### Replace removed GeoSeries methods

Do not call `GeoSeries.select`; the method has been removed because supported
pandas versions no longer provide its counterpart.

Replace:

```python
left.geom_almost_equals(right)
```

with:

```python
left.geom_equals_exact(right, tolerance)
```

The deprecated `geom_almost_equals` method is no longer available.

### Do not rely on point ordering

`sample_points` does not promise x-coordinate ordering. Treat the result as an
unordered collection of sampled points. If downstream code needs a particular
order, sort explicitly according to that application's rule.

### Expect DataFrame downcasting

Deleting the final geometry column changes a `GeoDataFrame` into a pandas
`DataFrame`:

```python
del gdf["geometry"]
```

Code that continues to require geospatial behavior must retain or create a
geometry column.

## Dependency compatibility

For an installation or CI failure, first compare the runtime and core packages
with the required floors. Optional-package floors describe tested support;
older optional versions might run but are unsupported.

Open [compatibility.md](references/compatibility.md) for the complete core and
optional dependency matrix.

## Spatial indexes

`SpatialIndex.query` can return boolean results in dense or sparse form:

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

Sparse output requires SciPy. Choose the format deliberately so downstream
code does not assume index-pair output.

## Union and dissolve choices

Use a precision grid when coordinates need snapping during a union:

```python
merged = frame.geometry.union_all(grid_size=0.01)
dissolved = frame.dissolve("group", grid_size=0.01)
```

Use the disjoint-subset algorithm when that method fits the input:

```python
merged = frame.geometry.union_all(method="disjoint_subset")
dissolved = frame.dissolve("group", method="disjoint_subset")
```

Both controls are available through `union_all` and `dissolve`. See
[geometry-operations.md](references/geometry-operations.md) for related
coverage and repair operations.

## Polygonal coverage workflow

Validate the coverage before simplifying it, and inspect invalid edges when
validation fails:

```python
valid = frame.geometry.is_valid_coverage()
invalid_edges = frame.geometry.invalid_coverage_edges()
simplified = frame.geometry.simplify_coverage(0.5)
```

These operations are exposed on both `GeoSeries` and `GeoDataFrame`.

## Geometry repair and measured coordinates

Choose the repair algorithm and collapsed-component behavior explicitly when
they matter:

```python
fixed = frame.geometry.make_valid(
    method="linework",
    keep_collapsed=True,
)
```

For measured geometries, use `m`, `has_m`, and `include_m=True`:

```python
measures = points.m
has_measures = frame.geometry.has_m
coordinates = frame.geometry.get_coordinates(include_m=True)
```

## Arrow-backed I/O

Pass pandas-conversion controls through `to_pandas_kwargs` when reading Arrow
data:

```python
frame = geopandas.read_parquet(
    "data.parquet",
    to_pandas_kwargs={"use_threads": False},
)
```

The option is accepted by `from_arrow`, `read_parquet`, and `read_feather`.
It also applies when non-geometry Parquet columns contain list or struct data.

Open [io-and-databases.md](references/io-and-databases.md) before handling
property-less features, CRS-less masks, missing string values, or PostGIS
geometry-column names.

## pandas interoperability

Import the accessor module to expose GeoSeries methods on
`pandas.Series.geo`:

```python
import geopandas.accessors

buffered = series.geo.buffer(10)
```

Named aggregation works for geometry columns through `GroupBy.agg`.

Be careful around pandas-driven state changes:

- a sole `np.nan` is accepted as missing geometry during construction;
- `GeoSeries.value_counts()` keeps the CRS on its result index;
- inserting a new row with `.loc` preserves geometry dtype and CRS;
- deleting the last geometry column downcasts to `DataFrame`;
- missing values from the pandas string dtype are handled by WKT, WKB, and
  PostGIS conversion paths.

See [pandas-integration.md](references/pandas-integration.md) for the exact
scope of each behavior.

## Overlay decisions

Identity overlays support matching non-geometry column names in both inputs.
Empty inputs are also handled more gracefully when `keep_geom_type` is used.

Before adding workarounds for either case, reproduce the issue on the installed
GeoPandas version and consult
[overlays-sampling-and-maps.md](references/overlays-sampling-and-maps.md).

## Reproducible point-pattern sampling

Point-pattern methods accept one sample size per geometry and an explicit
random state:

```python
sampled = geometries.sample_points(
    size=[10, 20],
    method="cluster_poisson",
    rng=42,
)
```

Use `rng` when repeatability matters. Never infer meaning from the generated
points' order.

## Interactive map legends

For categorical or boolean columns, provide custom labels through
`legend_kwds`:

```python
result = frame.explore(
    column="category",
    legend_kwds={"labels": ["First", "Second"]},
)
```

The labels are honored by `GeoDataFrame.explore()`.

## Diagnostic checklist

When behavior differs from expectations:

1. Confirm the installed GeoPandas, Python, and core dependency versions.
2. Identify whether the operation crosses into an optional dependency.
3. Check whether pandas object type, geometry dtype, active geometry, and CRS
   changed during the preceding operation.
4. For Arrow data, inspect non-geometry column types and conversion kwargs.
5. For overlays, test empty inputs, duplicate column names, and
   `keep_geom_type` separately.
6. For sampling, fix `rng` and avoid assumptions about point order.
7. Follow the matching topic reference before introducing a compatibility
   workaround.
