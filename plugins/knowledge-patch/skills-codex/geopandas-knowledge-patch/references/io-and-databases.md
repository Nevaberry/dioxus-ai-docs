# I/O and Databases

## Arrow-to-pandas conversion controls

Since 1.1.0, `from_arrow`, `read_parquet`, and `read_feather` accept
`to_pandas_kwargs`. The mapping controls conversion of non-geometry Arrow
data:

```python
frame = geopandas.read_parquet(
    "data.parquet",
    to_pandas_kwargs={"use_threads": False},
)
```

As of 1.1.2, `read_parquet` also supports this option when non-geometry Arrow
columns contain list or struct types.

## Features without properties

As of 1.1.2, `GeoDataFrame.from_features` accepts a feature that omits the
`properties` field. Code reading such features no longer needs to add an empty
properties mapping solely to avoid an exception.

## File masks and missing CRS

Since 1.1.0, `read_file` warns when a GeoDataFrame or GeoSeries mask lacks a
defined CRS, when the source dataset lacks one, or when both do. Treat the
warning as a prompt to establish the intended coordinate systems rather than
silencing it unconditionally.

## Missing strings in geometry conversion

As of 1.1.3, these paths correctly handle missing values when pandas 3
provides string data using its `str` dtype:

- `from_wkt`;
- `from_wkb`;
- `to_postgis`.

Avoid preprocessing missing string values merely to work around the earlier
dtype interaction.

## Safe PostGIS geometry column names

As of 1.1.2, `to_postgis` prevents SQL injection through the geometry column
name. Applications should still pass the intended geometry column name and
normal database identifiers, but do not need a separate workaround for this
specific injection path.
