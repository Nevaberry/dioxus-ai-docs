# Compatibility and pandas interop

## Dependencies

GeoPandas 1.1 requires Python 3.10+, pandas 2.0+, NumPy 1.24+, and pyproj
3.5+ (since 1.1.0).

The minimum tested optional versions are Fiona 1.8.21, SciPy 1.9, matplotlib
3.7, mapclassify 2.5, folium 0.12, and SQLAlchemy 2.0. Older optional versions
may work but are unsupported (since 1.1.0).

## Removed GeoSeries methods

`GeoSeries.select` is removed because the corresponding pandas method is not
available in supported pandas versions (since 1.1.0).

`geom_almost_equals` is removed. Replace it with `geom_equals_exact`
(since 1.1.0).

## Geometry construction and result types

Constructing geometry with `np.nan` as the only geometry works again. This
missing-only constructor regression was fixed in 1.1.1.

Deleting `gdf["geometry"]` downcasts the object to a pandas `DataFrame` when
no geometry columns remain (since 1.1.2).

## CRS retention

`GeoSeries.value_counts()` preserves the CRS on its result index
(since 1.1.2).

On pandas 3.1, assigning column values with `.loc` at a new row index preserves
the geometry column's CRS and geometry dtype (since 1.1.3).

## pandas 3 missing values

`from_wkt`, `from_wkb`, and `to_postgis` correctly handle missing values when
pandas 3 supplies string data using its new `str` dtype (since 1.1.3).
