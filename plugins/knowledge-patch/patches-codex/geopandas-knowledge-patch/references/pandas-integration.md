# pandas Integration

## Series geometry accessor

Since 1.1.0, importing `geopandas.accessors` registers `pandas.Series.geo`.
The accessor exposes GeoSeries methods through pandas's extension mechanism:

```python
import geopandas.accessors

buffered = series.geo.buffer(10)
```

Import the module before expecting `.geo` to be registered.

## Named geometry aggregation

Since 1.1.0, `GroupBy.agg` supports named aggregations over a geometry column.
Use pandas named-aggregation syntax when the output column needs an explicit
name.

## Removed GeoSeries methods

Two removals apply from 1.1.0:

- `GeoSeries.select` is removed because the corresponding pandas method is
  absent from supported pandas versions.
- `geom_almost_equals` is removed after deprecation. Use
  `geom_equals_exact` instead.

Do not add shims that assume either removed method remains available.

## Missing-only geometry construction

GeoPandas 1.1.1 restores construction when `np.nan` is the only supplied
geometry. The value represents missing geometry; it should not require a
non-missing placeholder.

## CRS-preserving value counts

As of 1.1.2, `GeoSeries.value_counts()` preserves the CRS on its index. Code
consuming the index can retain its coordinate-reference metadata.

## Removing the final geometry column

As of 1.1.2, deleting `gdf["geometry"]` downcasts the object to a pandas
`DataFrame` when no geometry columns remain:

```python
del gdf["geometry"]
```

Check the resulting object type if later code conditionally performs
geospatial operations.

## New-row assignment with pandas

As of 1.1.3, assigning column values with `.loc` at a new row index on pandas
3.1 preserves the geometry column's geometry dtype and CRS. A workaround that
reconstructs the geometry column after this form of insertion is not needed
for the fixed behavior.
