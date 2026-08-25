# Overlays, Sampling, and Maps

## Identity overlays with matching names

GeoPandas 1.1.1 restores `overlay(..., how="identity")` support when both input
GeoDataFrames contain columns with the same names. Duplicate input names alone
do not require pre-renaming as an overlay workaround.

## Empty-input overlays

As of 1.1.4, `overlay()` handles `keep_geom_type` more gracefully when either
input is empty. Test the empty-input result directly before preserving older
special-case handling.

## Point-pattern sampling controls

As of 1.1.3, `GeoSeries.sample_points` accepts list-like `size` values with
`pointpats` methods and accepts `rng` to set their random state:

```python
sampled = geometries.sample_points(
    size=[10, 20],
    method="cluster_poisson",
    rng=42,
)
```

A list-like size supplies per-geometry sample counts. Set `rng` for
reproducible point-pattern sampling.

## Point sampling order

As of 1.1.4, `sample_points` no longer sorts generated points by x-coordinate.
Do not treat output position as spatial ordering. Apply an explicit
application-defined sort if ordered points are required.

## Custom explore legend labels

As of 1.1.4, `GeoDataFrame.explore()` honors `legend_kwds={"labels": ...}` for
categorical and boolean columns:

```python
result = frame.explore(
    column="category",
    legend_kwds={"labels": ["First", "Second"]},
)
```
