# I/O and databases

## Arrow conversion controls

`from_arrow`, `read_parquet`, and `read_feather` accept `to_pandas_kwargs` for
controlling conversion of non-geometry Arrow data (since 1.1.0).

```python
frame = geopandas.read_parquet(
    "data.parquet",
    to_pandas_kwargs={"use_threads": False},
)
```

`read_parquet` also supports `to_pandas_kwargs` when non-geometry Arrow data
contains list or struct columns (since 1.1.2).

## File masks and CRS

`read_file` warns when a GeoDataFrame or GeoSeries mask, the source dataset,
or both have no defined CRS (since 1.1.0).

## Feature ingestion

`GeoDataFrame.from_features` accepts features that omit the `properties`
field instead of raising an error (since 1.1.2).

## PostGIS

`to_postgis` prevents SQL injection through the geometry column name
(since 1.1.2).

When pandas 3 supplies string data with its new `str` dtype, `to_postgis`
correctly handles missing values (since 1.1.3).
