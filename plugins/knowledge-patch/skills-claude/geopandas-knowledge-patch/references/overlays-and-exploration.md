# Overlays and exploration

## Identity overlays

`overlay(..., how="identity")` supports input GeoDataFrames that contain
columns with the same names. This behavior was restored in 1.1.1.

## Empty inputs

`overlay()` handles `keep_geom_type` more gracefully when an input is empty
(since 1.1.4).

## pandas Series geometry accessor

Import `geopandas.accessors` to register `pandas.Series.geo`, which exposes
GeoSeries methods through pandas's extension mechanism (since 1.1.0).

```python
import geopandas.accessors

buffered = series.geo.buffer(10)
```

## Explore legend labels

`GeoDataFrame.explore()` honors `legend_kwds={"labels": ...}` for categorical
and boolean columns (since 1.1.4).

```python
result = frame.explore(
    column="category",
    legend_kwds={"labels": ["First", "Second"]},
)
```
