# Multidimensional Data and Georeferencing

## Multidimensional discovery, views, and metadata

- **netCDF extra-dimension values (3.10.1).** Set
  `GDAL_NETCDF_REPORT_EXTRA_DIM_VALUES` when extra-dimension values should be
  reported.

- **Array discovery (3.11.0).** Zarr and netCDF support `LIST_ALL_ARRAYS`,
  defaulting to `NO`. Zarr reports compressor, filters, and array dimensions.
  netCDF can identify a geolocation array without a `coordinates` attribute
  and uses `GeoTransform` to retain precision.

- **Recursive array names (3.11.0).** Use
  `GDALGroup::GetMDArrayFullNamesRecursive()` to enumerate full multidimensional
  array names.

- **netCDF axis discovery (3.11.2).** The netCDF driver recognizes the axis of
  `rhos` variables in PACE OCI products and can use a geolocation array to find
  X and Y axes in three-dimensional variables.

- **HDF5 strides and auxiliary geolocation (3.11.4).** HDF5 multidimensional
  arrays support non-default read strides. Geolocation references from
  `.aux.xml` resolve correctly. For netCDF, `LIST_ALL_ARRAYS=YES` works even
  when no two-dimensional array exists.

- **Reverse slicing (3.11.5).** `CreateSlicedArray()` slices a dimension's
  indexing variables with its data. One-element dimensions work with
  `GetView(["::-1"])`, and `VRTMDArraySourceFromArray::Read()` handles negative
  steps.

- **Classic/multidimensional bridging (3.12.0).**
  `GDALDataset::AsMDArray()` presents a classic dataset as an array.
  `GDALMDArray::GetRawBlockInfo()` reports raw block information for HDF5,
  netCDF, Zarr, and VRT. Extended data types can expose raster attribute
  tables, groups can enumerate data types, and classic views can take band
  metadata from fully qualified attributes.

- **Multivalue conversion arguments (3.12.1).** `gdal mdim convert` accepts
  multiple `--group`, `--subset`, and `--scale-axes` values.

- **HDF5 swath metadata (3.12.1).** Swath geolocation fields are reported in
  the `GEOLOCATION` metadata domain instead of as ground control points.

- **Indexed multidimensional overviews (3.13.0).** Arrays expose
  `GetOverviewCount()` and indexed `GetOverview()` access.

- **Mosaic dimensions (3.13.0).** `gdal mdim mosaic` accepts dimensions that
  lack indexing variables; `gdal mdim info --summary` provides abbreviated
  output.

- **Sliced-array read advice (3.13.2).** Sliced arrays calculate the correct
  parent bounds for `IAdviseRead()` when the step is not one.

## Coordinate systems and transforms

- **Rotated latitude/longitude grids (3.11.1).** netCDF reads the spatial
  reference and geotransform from a Rotated Latitude Longitude grid mapping
  even when no ellipsoid is defined.

- **ESRI-labeled coordinate operations (3.11.2).** Coordinate transformation
  succeeds when an input CRS carries a code labeled EPSG that is actually an
  ESRI code.

- **Polar-to-geographic correction (3.11.5).** Core geometry transformation
  and `gdal vector reproject` correctly reproject from polar CRS coordinates to
  geographic coordinates.

- **Longitude normalization (3.12.0).** The geolocation transformer accepts
  `GEOLOC_NORMALIZE_LONGITUDE_MINUS_180_PLUS_180` to force longitudes into the
  -180 to +180 interval.

- **GCP transformer options (3.12.2).** `GDALTransformer()` ignores
  `MAX_GCP_ORDER` with `METHOD=GCP_TPS`; with
  `METHOD=GCP_POLYNOMIAL`, it sanitizes negative `MAX_GCP_ORDER` values.

- **Homography overview scaling (3.12.3).** Homography GCP transforms apply
  the correct scaling factor on overviews.

- **Stored geotransform validation (3.12.3).** netCDF uses a stored
  `GeoTransform` only when it agrees with dimension variables. RPFTOC now
  georeferences polar zones correctly.

- **Vertical-shift unit metadata (3.13.1).** A 3D-to-3D vertical-shift warp no
  longer copies the source unit type into the output.

## HDF and product geolocation details

- **HDF4 nodata GCPs (3.11.5).** HDF4 skips longitude and latitude values at
  nodata positions when generating ground control points.

- **S-102 depth-only products (3.11.1).** S102 opens products without an
  uncertainty component and retrieves nodata correctly when only depth is
  present.

- **Sentinel-2 missing granules (3.12.2).** Geolocation-enabled Sentinel-2
  subdatasets tolerate expected missing granules.

- **MiraMon multiband transforms (3.12.2).** MiraMonRaster reports the correct
  dataset geotransform for multiband data.

- **NITF RPFIMG coordinates (3.12.2).** NITF specification data uses corrected
  latitude/longitude ordering in the RPFIMG `CoverageSectionSubheader`.

- **DIMAP2 coverage metadata (3.13.2).** DIMAP2 reports `CLOUD_COVERAGE` and
  `SNOW_COVERAGE` metadata.

- **S-10x enumeration names (3.13.3).** S102, S104, and S111 writers and
  validators use corrected `dataCodingFormat` enumeration names.

## Subdataset and path parsing

- **Connection and endpoint parsing (3.12.3).** GeoRaster preserves double
  quotes in database connection strings. `GDALGetSubdatasetInfo()` handles a
  netCDF subdataset endpoint containing a port number.

- **Multiple colons in netCDF paths (3.13.3).** netCDF parses subdataset names
  correctly when the underlying path contains multiple colons.
