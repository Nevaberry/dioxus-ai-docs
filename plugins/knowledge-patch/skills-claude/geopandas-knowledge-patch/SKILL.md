---
name: geopandas-knowledge-patch
description: GeoPandas
version: 1.1.4
license: MIT
metadata:
  author: Nevaberry
---


# GeoPandas Compatibility Guidance

Use this skill to make GeoPandas dependency, migration, geometry-operation,
I/O, database, overlay, and visualization decisions.

## Working method

1. Inspect the project's GeoPandas, Python, pandas, NumPy, pyproj, and optional
   dependency constraints.
2. Read the reference file that matches the task before changing code.
3. Check removed APIs and behavior changes before diagnosing a regression.
4. Preserve CRS and geometry dtype explicitly when testing pandas interop.
5. Treat ordering as significant only where the relevant API guarantees it.
6. Add focused tests for the compatibility case being changed.

## Reference index

| Reference | Topics |
| --- | --- |
| [Compatibility and pandas interop](references/compatibility-and-pandas.md) | Dependency floors, removed methods, constructors, CRS retention, geometry-column removal, pandas 3 behavior |
| [Geometry operations](references/geometry-operations.md) | Spatial indexes, union and dissolve, coverage tools, validity repair, M coordinates, sampling, geometry aggregation |
| [I/O and databases](references/io-and-databases.md) | Arrow conversion, Parquet and Feather, file masks, feature ingestion, PostGIS |
| [Overlays and exploration](references/overlays-and-exploration.md) | Identity and empty overlays, pandas geometry accessor, explore legend labels |

## Breaking changes and dependency floors

Require these core versions:

- Python 3.10 or newer
- pandas 2.0 or newer
- NumPy 1.24 or newer
- pyproj 3.5 or newer

The optional versions tested at minimum are Fiona 1.8.21, SciPy 1.9,
matplotlib 3.7, mapclassify 2.5, folium 0.12, and SQLAlchemy 2.0.
Older optional versions may work, but are unsupported.

Replace removed `GeoSeries` methods:

```python
# Removed: series.geom_almost_equals(other)
matches = series.geom_equals_exact(other, tolerance)
```

Do not call `GeoSeries.select`; it was removed because supported pandas
versions no longer provide the corresponding method.

Deleting the last geometry column changes the container type:

```python
del gdf["geometry"]
# gdf is now a pandas DataFrame when no geometry columns remain.
```

Read
[Compatibility and pandas interop](references/compatibility-and-pandas.md)
when upgrading dependencies or debugging dtype, CRS, construction, or
missing-value behavior.

## Spatial-index result formats

Choose the `SpatialIndex.query` representation with `output_format`:

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

The sparse boolean representation requires SciPy. Select dense or sparse
deliberately rather than assuming one representation.

## Union and dissolve controls

Apply a precision grid during union or grouped dissolve:

```python
merged = frame.geometry.union_all(grid_size=0.01)
dissolved = frame.dissolve("group", grid_size=0.01)
```

Select the disjoint-subset union algorithm where appropriate:

```python
merged = frame.geometry.union_all(method="disjoint_subset")
dissolved = frame.dissolve(
    "group",
    method="disjoint_subset",
)
```

See [Geometry operations](references/geometry-operations.md) for the related
coverage, repair, coordinate, sampling, and aggregation APIs.

## Polygonal coverage and repair

Validate and simplify polygonal coverages with the coverage-specific methods:

```python
valid = frame.geometry.is_valid_coverage()
invalid_edges = frame.geometry.invalid_coverage_edges()
simplified = frame.geometry.simplify_coverage(0.5)
```

Control geometry repair with `method` and `keep_collapsed`:

```python
fixed = frame.geometry.make_valid(
    method="linework",
    keep_collapsed=True,
)
```

Choose these options explicitly when the repair algorithm or treatment of
collapsed components matters.

## Measured coordinates

Use `m` and `has_m` for measured-coordinate access:

```python
measures = points.m
has_measures = frame.geometry.has_m
```

Include M values when extracting coordinates:

```python
coordinates = frame.geometry.get_coordinates(
    include_m=True,
)
```

## Arrow conversion

Pass pandas conversion controls through Arrow-backed readers and constructors
with `to_pandas_kwargs`:

```python
frame = geopandas.read_parquet(
    "data.parquet",
    to_pandas_kwargs={"use_threads": False},
)
```

The option is accepted by `from_arrow`, `read_parquet`, and `read_feather`.
It also applies when non-geometry Parquet columns contain list or struct data.

Read [I/O and databases](references/io-and-databases.md) before changing
Arrow conversion, file-mask CRS handling, feature ingestion, or PostGIS code.

## Point sampling

Use list-like `size` with `pointpats` methods for per-geometry sample counts,
and use `rng` for reproducible sampling:

```python
sampled = geometries.sample_points(
    size=[10, 20],
    method="cluster_poisson",
    rng=42,
)
```

Do not assume sampled points are ordered by x-coordinate. Generated points
are no longer sorted that way.

## Overlay and exploration checks

Identity overlays support matching input column names. Empty-input overlays
handle `keep_geom_type` more gracefully.

For categorical or boolean exploration maps, provide custom legend labels:

```python
result = frame.explore(
    column="category",
    legend_kwds={"labels": ["First", "Second"]},
)
```

Read [Overlays and exploration](references/overlays-and-exploration.md) for
overlay edge cases and pandas Series geometry access.

## Verification checklist

- Confirm core and optional dependency constraints.
- Search for removed `select` and `geom_almost_equals` calls.
- Test CRS retention after pandas operations.
- Test the result type after removing geometry columns.
- Exercise missing geometries and missing string values.
- Check sparse-index paths with SciPy installed.
- Test union precision and algorithm selection separately.
- Validate Arrow conversion with representative nested columns.
- Verify overlay behavior with duplicate column names and empty inputs.
- Avoid assertions that depend on sampled-point x ordering.
